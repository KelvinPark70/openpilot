#!/usr/bin/env python3
import math
import numpy as np
from common.params import Params, put_nonblocking
from common.numpy_fast import interp

import cereal.messaging as messaging
from cereal import car
from common.realtime import sec_since_boot
from selfdrive.swaglog import cloudlog
from selfdrive.config import Conversions as CV
from selfdrive.controls.lib.speed_smoother import speed_smoother
from selfdrive.controls.lib.longcontrol import LongCtrlState, MIN_CAN_SPEED
from selfdrive.controls.lib.fcw import FCWChecker
from selfdrive.controls.lib.long_mpc import LongitudinalMpc
from common.dp import get_last_modified

MAX_SPEED = 255.0

LON_MPC_STEP = 0.2  # first step is 0.2s
MAX_SPEED_ERROR = 2.0
AWARENESS_DECEL = -0.2     # car smoothly decel at .2m/s^2 when user is distracted

# lookup tables VS speed to determine min and max accels in cruise
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MIN_V  = [-1.0, -.8, -.67, -.5, -.30]
_A_CRUISE_MIN_BP = [   0., 5.,  10., 20.,  40.]

# need fast accel at very low speed for stop and go
# make sure these accelerations are smaller than mpc limits
_A_CRUISE_MAX_V = [1.2, 1.2, 0.65, .4]
_A_CRUISE_MAX_V_FOLLOWING = [1.6, 1.6, 0.65, .4]
_A_CRUISE_MAX_BP = [0.,  6.4, 22.5, 40.]

# Lookup table for turns
_A_TOTAL_MAX_V = [1.7, 3.2]
_A_TOTAL_MAX_BP = [20., 40.]

# 75th percentile
SPEED_PERCENTILE_IDX = 7


# dp
# accel profile by @arne182
_AP_CRUISE_MIN_V = [-2.0, -1.5, -1.0, -0.7, -0.5]
_AP_CRUISE_MIN_V_ECO = [-1.0, -0.7, -0.6, -0.5, -0.3]
_AP_CRUISE_MIN_V_SPORT = [-3.0, -2.6, -2.3, -2.0, -1.0]
_AP_CRUISE_MIN_V_FOLLOWING = [-4.0, -4.0, -3.5, -2.5, -2.0]
_AP_CRUISE_MIN_BP = [0.0, 5.0, 10.0, 20.0, 55.0]

_AP_CRUISE_MAX_V = [2.0, 2.0, 1.5, .5, .3]
_AP_CRUISE_MAX_V_ECO = [0.8, 0.9, 1.0, 0.4, 0.2]
_AP_CRUISE_MAX_V_SPORT = [3.0, 3.5, 3.0, 2.0, 2.0]
_AP_CRUISE_MAX_V_FOLLOWING = [1.6, 1.4, 1.4, .7, .3]
_AP_CRUISE_MAX_BP = [0., 5., 10., 20., 55.]

# Lookup table for turns
_AP_TOTAL_MAX_V = [3.3, 3.0, 3.9]
_AP_TOTAL_MAX_BP = [0., 25., 55.]

AP_OFF = 0
AP_ECO = 1
AP_NORMAL = 2
AP_SPORT = 3


def calc_cruise_accel_limits(v_ego, following, accel_profile):
  if accel_profile == AP_OFF:
    a_cruise_min = interp(v_ego, _A_CRUISE_MIN_BP, _A_CRUISE_MIN_V)

    if following:
      a_cruise_max = interp(v_ego, _A_CRUISE_MAX_BP, _A_CRUISE_MAX_V_FOLLOWING)
    else:
      a_cruise_max = interp(v_ego, _A_CRUISE_MAX_BP, _A_CRUISE_MAX_V)
  else:
    if following:
      a_cruise_min = interp(v_ego, _AP_CRUISE_MIN_BP, _AP_CRUISE_MIN_V_FOLLOWING)
      a_cruise_max = interp(v_ego, _AP_CRUISE_MAX_BP, _AP_CRUISE_MAX_V_FOLLOWING)
    else:
      if accel_profile == AP_ECO:
        a_cruise_min = interp(v_ego, _AP_CRUISE_MIN_BP, _AP_CRUISE_MIN_V_ECO)
        a_cruise_max = interp(v_ego, _AP_CRUISE_MAX_BP, _AP_CRUISE_MAX_V_ECO)
      elif accel_profile == AP_SPORT:
        a_cruise_min = interp(v_ego, _AP_CRUISE_MIN_BP, _AP_CRUISE_MIN_V_SPORT)
        a_cruise_max = interp(v_ego, _AP_CRUISE_MAX_BP, _AP_CRUISE_MAX_V_SPORT)
      else:
        a_cruise_min = interp(v_ego, _AP_CRUISE_MIN_BP, _AP_CRUISE_MIN_V)
        a_cruise_max = interp(v_ego, _AP_CRUISE_MAX_BP, _AP_CRUISE_MAX_V)
  return np.vstack([a_cruise_min, a_cruise_max])


def limit_accel_in_turns(v_ego, angle_steers, a_target, CP, accel_profile):
  """
  This function returns a limited long acceleration allowed, depending on the existing lateral acceleration
  this should avoid accelerating when losing the target in turns
  """
  if accel_profile == AP_OFF:
    a_total_max = interp(v_ego, _A_TOTAL_MAX_BP, _A_TOTAL_MAX_V)
  else:
    a_total_max = interp(v_ego, _AP_TOTAL_MAX_BP, _AP_TOTAL_MAX_V)
  a_y = v_ego**2 * angle_steers * CV.DEG_TO_RAD / (CP.steerRatio * CP.wheelbase)
  a_x_allowed = math.sqrt(max(a_total_max**2 - a_y**2, 0.))

  return [a_target[0], min(a_target[1], a_x_allowed)]


class Planner():
  def __init__(self, CP):
    self.CP = CP

    self.mpc1 = LongitudinalMpc(1)
    self.mpc2 = LongitudinalMpc(2)

    self.v_acc_start = 0.0
    self.a_acc_start = 0.0

    self.v_acc = 0.0
    self.v_acc_future = 0.0
    self.a_acc = 0.0
    self.v_cruise = 0.0
    self.a_cruise = 0.0
    self.v_model = 0.0
    self.a_model = 0.0

    self.longitudinalPlanSource = 'cruise'
    self.fcw_checker = FCWChecker()
    self.path_x = np.arange(192)

    self.params = Params()
    self.first_loop = True

    # dp
    self.dragon_slow_on_curve = True
    self.dragon_alt_accel_profile = False
    self.dragon_fast_accel = False
    self.dragon_accel_profile = AP_OFF
    self.last_ts = 0.
    self.dp_last_modified = None

  def choose_solution(self, v_cruise_setpoint, enabled):
    if enabled:
      solutions = {'model': self.v_model, 'cruise': self.v_cruise}
      if self.mpc1.prev_lead_status:
        solutions['mpc1'] = self.mpc1.v_mpc
      if self.mpc2.prev_lead_status:
        solutions['mpc2'] = self.mpc2.v_mpc

      slowest = min(solutions, key=solutions.get)

      self.longitudinalPlanSource = slowest
      # Choose lowest of MPC and cruise
      if slowest == 'mpc1':
        self.v_acc = self.mpc1.v_mpc
        self.a_acc = self.mpc1.a_mpc
      elif slowest == 'mpc2':
        self.v_acc = self.mpc2.v_mpc
        self.a_acc = self.mpc2.a_mpc
      elif slowest == 'cruise':
        self.v_acc = self.v_cruise
        self.a_acc = self.a_cruise
      elif slowest == 'model':
        self.v_acc = self.v_model
        self.a_acc = self.a_model

    self.v_acc_future = min([self.mpc1.v_mpc_future, self.mpc2.v_mpc_future, v_cruise_setpoint])

  def update(self, sm, pm, CP, VM, PP):
    """Gets called when new radarState is available"""
    cur_time = sec_since_boot()
    v_ego = sm['carState'].vEgo

    # dp
    # update variable status every 5 secs
    if cur_time - self.last_ts >= 5.:
      modified = get_last_modified()
      if self.dp_last_modified != modified:
        self.dragon_slow_on_curve = False if self.params.get("DragonEnableSlowOnCurve", encoding='utf8') == "0" else True
        try:
          self.dragon_accel_profile = int(self.params.get("DragonAccelProfile", encoding='utf8').rstrip('\x00'))
        except (TypeError, ValueError):
          self.dragon_accel_profile = AP_OFF
          put_nonblocking('DragonAccelProfile', AP_OFF)
        self.dp_last_modified = modified
      self.last_ts = cur_time

    long_control_state = sm['controlsState'].longControlState
    v_cruise_kph = sm['controlsState'].vCruise
    force_slow_decel = sm['controlsState'].forceDecel
    v_cruise_setpoint = v_cruise_kph * CV.KPH_TO_MS

    lead_1 = sm['radarState'].leadOne
    lead_2 = sm['radarState'].leadTwo

    enabled = (long_control_state == LongCtrlState.pid) or (long_control_state == LongCtrlState.stopping)
    following = lead_1.status and lead_1.dRel < 45.0 and lead_1.vLeadK > v_ego and lead_1.aLeadK > 0.0

    if self.dragon_slow_on_curve and len(sm['model'].path.poly):
      path = list(sm['model'].path.poly)

      # Curvature of polynomial https://en.wikipedia.org/wiki/Curvature#Curvature_of_the_graph_of_a_function
      # y = a x^3 + b x^2 + c x + d, y' = 3 a x^2 + 2 b x + c, y'' = 6 a x + 2 b
      # k = y'' / (1 + y'^2)^1.5
      # TODO: compute max speed without using a list of points and without numpy
      y_p = 3 * path[0] * self.path_x**2 + 2 * path[1] * self.path_x + path[2]
      y_pp = 6 * path[0] * self.path_x + 2 * path[1]
      curv = y_pp / (1. + y_p**2)**1.5

      a_y_max = 2.975 - v_ego * 0.0375  # ~1.85 @ 75mph, ~2.6 @ 25mph
      v_curvature = np.sqrt(a_y_max / np.clip(np.abs(curv), 1e-4, None))
      model_speed = np.min(v_curvature)
      model_speed = max(20.0 * CV.MPH_TO_MS, model_speed) # Don't slow down below 20mph
    else:
      model_speed = MAX_SPEED

    # Calculate speed for normal cruise control
    if enabled and not self.first_loop:
      accel_limits = [float(x) for x in calc_cruise_accel_limits(v_ego, following, self.dragon_accel_profile)]
      jerk_limits = [min(-0.1, accel_limits[0]), max(0.1, accel_limits[1])]  # TODO: make a separate lookup for jerk tuning
      accel_limits_turns = limit_accel_in_turns(v_ego, sm['carState'].steeringAngle, accel_limits, self.CP, self.dragon_accel_profile)

      if force_slow_decel:
        # if required so, force a smooth deceleration
        accel_limits_turns[1] = min(accel_limits_turns[1], AWARENESS_DECEL)
        accel_limits_turns[0] = min(accel_limits_turns[0], accel_limits_turns[1])

      self.v_cruise, self.a_cruise = speed_smoother(self.v_acc_start, self.a_acc_start,
                                                    v_cruise_setpoint,
                                                    accel_limits_turns[1], accel_limits_turns[0],
                                                    jerk_limits[1], jerk_limits[0],
                                                    LON_MPC_STEP)

      self.v_model, self.a_model = speed_smoother(self.v_acc_start, self.a_acc_start,
                                                    model_speed,
                                                    2*accel_limits[1], accel_limits[0],
                                                    2*jerk_limits[1], jerk_limits[0],
                                                    LON_MPC_STEP)

      # cruise speed can't be negative even is user is distracted
      self.v_cruise = max(self.v_cruise, 0.)
    else:
      starting = long_control_state == LongCtrlState.starting
      a_ego = min(sm['carState'].aEgo, 0.0)
      reset_speed = MIN_CAN_SPEED if starting else v_ego
      reset_accel = self.CP.startAccel if starting else a_ego
      self.v_acc = reset_speed
      self.a_acc = reset_accel
      self.v_acc_start = reset_speed
      self.a_acc_start = reset_accel
      self.v_cruise = reset_speed
      self.a_cruise = reset_accel

    self.mpc1.set_cur_state(self.v_acc_start, self.a_acc_start)
    self.mpc2.set_cur_state(self.v_acc_start, self.a_acc_start)

    self.mpc1.update(pm, sm['carState'], lead_1, v_cruise_setpoint)
    self.mpc2.update(pm, sm['carState'], lead_2, v_cruise_setpoint)

    self.choose_solution(v_cruise_setpoint, enabled)

    # determine fcw
    if self.mpc1.new_lead:
      self.fcw_checker.reset_lead(cur_time)

    blinkers = sm['carState'].leftBlinker or sm['carState'].rightBlinker
    fcw = self.fcw_checker.update(self.mpc1.mpc_solution, cur_time,
                                  sm['controlsState'].active,
                                  v_ego, sm['carState'].aEgo,
                                  lead_1.dRel, lead_1.vLead, lead_1.aLeadK,
                                  lead_1.yRel, lead_1.vLat,
                                  lead_1.fcw, blinkers) and not sm['carState'].brakePressed
    if fcw:
      cloudlog.info("FCW triggered %s", self.fcw_checker.counters)

    radar_dead = not sm.alive['radarState']

    radar_errors = list(sm['radarState'].radarErrors)
    radar_fault = car.RadarData.Error.fault in radar_errors
    radar_can_error = car.RadarData.Error.canError in radar_errors

    # **** send the plan ****
    plan_send = messaging.new_message('plan')

    plan_send.valid = sm.all_alive_and_valid(service_list=['carState', 'controlsState', 'radarState'])

    plan_send.plan.mdMonoTime = sm.logMonoTime['model']
    plan_send.plan.radarStateMonoTime = sm.logMonoTime['radarState']

    # longitudal plan
    plan_send.plan.vCruise = float(self.v_cruise)
    plan_send.plan.aCruise = float(self.a_cruise)
    plan_send.plan.vStart = float(self.v_acc_start)
    plan_send.plan.aStart = float(self.a_acc_start)
    plan_send.plan.vTarget = float(self.v_acc)
    plan_send.plan.aTarget = float(self.a_acc)
    plan_send.plan.vTargetFuture = float(self.v_acc_future)
    plan_send.plan.hasLead = self.mpc1.prev_lead_status
    plan_send.plan.longitudinalPlanSource = self.longitudinalPlanSource

    radar_valid = not (radar_dead or radar_fault)
    plan_send.plan.radarValid = bool(radar_valid)
    plan_send.plan.radarCanError = bool(radar_can_error)

    plan_send.plan.processingDelay = (plan_send.logMonoTime / 1e9) - sm.rcv_time['radarState']

    # Send out fcw
    plan_send.plan.fcw = fcw

    pm.send('plan', plan_send)

    # Interpolate 0.05 seconds and save as starting point for next iteration
    a_acc_sol = self.a_acc_start + (CP.radarTimeStep / LON_MPC_STEP) * (self.a_acc - self.a_acc_start)
    v_acc_sol = self.v_acc_start + CP.radarTimeStep * (a_acc_sol + self.a_acc_start) / 2.0
    self.v_acc_start = v_acc_sol
    self.a_acc_start = a_acc_sol

    self.first_loop = False
