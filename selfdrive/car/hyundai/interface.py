#!/usr/bin/env python3
from cereal import car
from selfdrive.config import Conversions as CV
from selfdrive.controls.lib.drive_helpers import EventTypes as ET, create_event
from selfdrive.car.hyundai.values import Ecu, ECU_FINGERPRINT, CAR, FINGERPRINTS
from selfdrive.car import STD_CARGO_KG, scale_rot_inertia, scale_tire_stiffness, is_ecu_disconnected, gen_empty_fingerprint
from selfdrive.car.interfaces import CarInterfaceBase

GearShifter = car.CarState.GearShifter

class CarInterface(CarInterfaceBase):
  def __init__(self, CP, CarController, CarState):
    super().__init__(CP, CarController, CarState)
    self.cp2 = self.CS.get_can2_parser(CP)
    self.lkas_button_alert = False

  @staticmethod
  def compute_gb(accel, speed):
    return float(accel) / 3.0

  @staticmethod
  def get_params(candidate, fingerprint=gen_empty_fingerprint(), has_relay=False, car_fw=[]):
    ret = CarInterfaceBase.get_std_params(candidate, fingerprint, has_relay)

    ret.carName = "hyundai"
    ret.safetyModel = car.CarParams.SafetyModel.hyundai

    # Hyundai port is a community feature for now
    ret.communityFeature = False

    ret.steerActuatorDelay = 0.1  # Default delay
    ret.steerRateCost = 0.5
    ret.steerLimitTimer = 0.8
    tire_stiffness_factor = 1.

    if candidate in [CAR.SANTAFE, CAR.SANTAFE_1]:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1830. + STD_CARGO_KG
      ret.wheelbase = 2.765
      # Values from optimizer
      ret.steerRatio = 13.8  # 13.8 is spec end-to-end
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.SORENTO:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1950. + STD_CARGO_KG
      ret.wheelbase = 2.78
      ret.steerRatio = 14.4 * 1.15
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate in [CAR.AVANTE, CAR.I30]:
      ret.lateralTuning.pid.kf = 0.00006
      ret.mass = 1275. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73   #Spec
      tire_stiffness_factor = 0.385
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.GENESIS:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 2060. + STD_CARGO_KG
      ret.wheelbase = 3.01
      ret.steerRatio = 16.5
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.16], [0.01]]
    elif candidate in [CAR.GENESIS_G90, CAR.GENESIS_G80]:
      ret.mass = 2200
      ret.wheelbase = 3.15
      ret.steerRatio = 12.069
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.16], [0.01]]
    elif candidate in [CAR.K5, CAR.SONATA]:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1470. + STD_CARGO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 12.75
      ret.steerRateCost = 0.4
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.SONATA_TURBO:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1565. + STD_CARGO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 14.4 * 1.15   # 15% higher at the center seems reasonable
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate in [CAR.K5_HYBRID, CAR.SONATA_HYBRID]:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1595. + STD_CARGO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 12.75
      ret.steerRateCost = 0.45
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.22], [0.04]]
    elif candidate in [CAR.GRANDEUR, CAR.K7]:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1570. + STD_CARGO_KG
      ret.wheelbase = 2.885
      ret.steerRatio = 12.5
      ret.steerRateCost = 0.4
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate in [CAR.GRANDEUR_HYBRID, CAR.K7_HYBRID]:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1675. + STD_CARGO_KG
      ret.wheelbase = 2.885
      ret.steerRatio = 12.5
      ret.steerRateCost = 0.4
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.20], [0.03]]   # [[0.25], [0.05]]
    elif candidate == CAR.STINGER:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1825. + STD_CARGO_KG
      ret.wheelbase = 2.78
      ret.steerRatio = 14.4 * 1.15   # 15% higher at the center seems reasonable
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.KONA:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1330. + STD_CARGO_KG
      ret.wheelbase = 2.6
      ret.steerRatio = 13.5   #Spec
      ret.steerRateCost = 0.4
      tire_stiffness_factor = 0.385
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.KONA_EV:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1330. + STD_CARGO_KG
      ret.wheelbase = 2.6
      ret.steerRatio = 13.5   #Spec
      ret.steerRateCost = 0.4
      tire_stiffness_factor = 0.385
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.NIRO:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1425. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73   #Spec
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.NIRO_EV:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1425. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73   #Spec
      tire_stiffness_factor = 0.385
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.IONIQ:
      ret.lateralTuning.pid.kf = 0.00006
      ret.mass = 1275. + STD_CARGO_KG
      ret.wheelbase = 2.7
      ret.steerRatio = 13.73   #Spec
      tire_stiffness_factor = 0.385
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.IONIQ_EV:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1490. + STD_CARGO_KG   #weight per hyundai site https://www.hyundaiusa.com/ioniq-electric/specifications.aspx
      ret.wheelbase = 2.7
      ret.steerRatio = 13.25   #Spec
      ret.steerRateCost = 0.4
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.K3:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 3558. * CV.LB_TO_KG
      ret.wheelbase = 2.80
      ret.steerRatio = 13.75
      tire_stiffness_factor = 0.5
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.NEXO:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1885. + STD_CARGO_KG
      ret.wheelbase = 2.79
      ret.steerRatio = 12.5
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]
    elif candidate == CAR.SELTOS:
      ret.lateralTuning.pid.kf = 0.00005
      ret.mass = 1470. + STD_CARGO_KG
      ret.wheelbase = 2.63
      ret.steerRatio = 13.0
      ret.lateralTuning.pid.kiBP, ret.lateralTuning.pid.kpBP = [[0.], [0.]]
      ret.lateralTuning.pid.kpV, ret.lateralTuning.pid.kiV = [[0.25], [0.05]]

    ret.minEnableSpeed = -1.   # enable is done by stock ACC, so ignore this

    ret.centerToFront = ret.wheelbase * 0.4

    # TODO: get actual value, for now starting with reasonable value for
    # civic and scaling by mass and wheelbase
    ret.rotationalInertia = scale_rot_inertia(ret.mass, ret.wheelbase)

    # TODO: start from empirically derived lateral slip stiffness for the civic and scale by
    # mass and CG position, so all cars will have approximately similar dyn behaviors
    ret.tireStiffnessFront, ret.tireStiffnessRear = scale_tire_stiffness(ret.mass, ret.wheelbase, ret.centerToFront,
                                                                         tire_stiffness_factor=tire_stiffness_factor)


    # no rear steering, at least on the listed cars above
    ret.steerRatioRear = 0.
    ret.steerControlType = car.CarParams.SteerControlType.torque

    ret.longitudinalTuning.kpBP = [0., 5., 35.]
    ret.longitudinalTuning.kpV = [1.2, 0.8, 0.5]
    ret.longitudinalTuning.kiBP = [0., 35.]
    ret.longitudinalTuning.kiV = [0.18, 0.12]
    ret.longitudinalTuning.deadzoneBP = [0.]
    ret.longitudinalTuning.deadzoneV = [0.]


    # steer, gas, brake limitations VS speed
    ret.steerMaxBP = [0.]
    ret.steerMaxV = [1.0]
    ret.gasMaxBP = [0.]
    ret.gasMaxV = [0.5]
    ret.brakeMaxBP = [0., 20.]
    ret.brakeMaxV = [1., 0.8]

    ret.enableCamera = is_ecu_disconnected(fingerprint[0], FINGERPRINTS, ECU_FINGERPRINT, candidate, Ecu.fwdCamera) or has_relay

    ret.stoppingControl = True
    ret.startAccel = 0.0

    # ignore CAN2 address if L-CAN on the same BUS
    ret.mdpsBus = 1 if 593 in fingerprint[1] and 1296 not in fingerprint[1] else 0
    ret.sasBus = 1 if 688 in fingerprint[1] and 1296 not in fingerprint[1] else 0
    ret.sccBus = 0 if 1056 in fingerprint[0] else 1 if 1056 in fingerprint[1] and 1296 not in fingerprint[1] \
                                                                     else 2 if 1056 in fingerprint[2] else -1
    ret.radarOffCan = ret.sccBus == -1
    ret.openpilotLongitudinalControl = bool(ret.sccBus and not ret.radarOffCan)
    ret.autoLcaEnabled = True

    return ret

  def update(self, c, can_strings):
    self.dp_load_params('hyundai')
    self.cp.update_strings(can_strings)
    self.cp2.update_strings(can_strings)
    self.cp_cam.update_strings(can_strings)

    ret = self.CS.update(self.cp, self.cp2, self.cp_cam)
    ret.canValid = self.cp.can_valid and self.cp2.can_valid and self.cp_cam.can_valid

    # most HKG cars has no long control, it is safer and easier to engage by main on
    ret.cruiseState.enabled = ret.cruiseState.available if not self.CC.longcontrol else ret.cruiseState.enabled

    if self.CS.left_blinker_flash or self.CS.prev_left_blinker and self.CC.turning_signal_timer:
      ret.leftBlinker = True
    if self.CS.right_blinker_flash or self.CS.prev_right_blinker and self.CC.turning_signal_timer:
      ret.rightBlinker = True

    # turning indicator alert logic
    if (ret.leftBlinker or ret.rightBlinker or self.CC.turning_signal_timer) and ret.vEgo < 20.1168:
      self.turning_indicator_alert = True 
    else:
      self.turning_indicator_alert = False

    # low speed steer alert hysteresis logic (only for cars with steer cut off above 10 m/s)
    if ret.vEgo < (self.CP.minSteerSpeed + 0.2) and self.CP.minSteerSpeed > 10.:
      self.low_speed_alert = True
    if ret.vEgo > (self.CP.minSteerSpeed + 0.7):
      self.low_speed_alert = False

    # TODO: button presses
    ret.buttonEvents = []

    #events = self.create_common_events(ret)
    #TODO: addd abs(self.CS.angle_steers) > 90 to 'steerTempUnavailable' event

    events = []
    if not ret.gearShifter == GearShifter.drive:
      events.append(create_event('wrongGear', [ET.NO_ENTRY, ET.USER_DISABLE]))
    if ret.doorOpen:
      events.append(create_event('doorOpen', [ET.NO_ENTRY, ET.SOFT_DISABLE]))
    if ret.seatbeltUnlatched:
      events.append(create_event('seatbeltNotLatched', [ET.NO_ENTRY, ET.SOFT_DISABLE]))
    if ret.espDisabled:
      events.append(create_event('espDisabled', [ET.NO_ENTRY, ET.SOFT_DISABLE]))
    if not ret.cruiseState.available:
      events.append(create_event('wrongCarMode', [ET.NO_ENTRY, ET.USER_DISABLE]))
    if ret.gearShifter == GearShifter.reverse:
      events.append(create_event('reverseGear', [ET.NO_ENTRY, ET.USER_DISABLE]))
    #if self.CS.steer_warning or abs(ret.steeringAngle) > 90.:
      #events.append(create_event('steerTempUnavailable', [ET.NO_ENTRY, ET.WARNING]))

    if ret.cruiseState.enabled and not self.CS.out.cruiseState.enabled:
      events.append(create_event('pcmEnable', [ET.ENABLE]))
    elif not ret.cruiseState.enabled:
      events.append(create_event('pcmDisable', [ET.USER_DISABLE]))

    # disable on pedals rising edge or when brake is pressed and speed isn't zero
    if ((ret.gasPressed and not self.CS.out.gasPressed) or \
      (ret.brakePressed and (not self.CS.out.brakePressed or ret.vEgoRaw > 0.1))) and self.CC.longcontrol:
      events.append(create_event('pedalPressed', [ET.NO_ENTRY, ET.USER_DISABLE]))

    if ret.gasPressed and self.CC.longcontrol:
      events.append(create_event('pedalPressed', [ET.PRE_ENABLE]))

    if self.low_speed_alert and not self.CS.mdps_bus :
      events.append(create_event('belowSteerSpeed', [ET.WARNING]))
    if self.turning_indicator_alert:
      events.append(create_event('turningIndicatorOn', [ET.WARNING]))
    #TODO Varible for min Speed for LCA
    if ret.rightBlinker and ret.rightBlindspot and ret.vEgo > (45 * CV.MPH_TO_MS):
      events.append(create_event('rightLCAbsm', [ET.WARNING]))
    if ret.leftBlinker and ret.leftBlindspot and ret.vEgo > (45 * CV.MPH_TO_MS):
      events.append(create_event('leftLCAbsm', [ET.WARNING]))

    ret.events = events

    self.CS.out = ret.as_reader()
    return self.CS.out

  def apply(self, c):
    can_sends = self.CC.update(c.enabled, self.CS, self.frame, c.actuators,
                               c.cruiseControl.cancel, c.hudControl.visualAlert, c.hudControl.leftLaneVisible,
                               c.hudControl.rightLaneVisible, c.hudControl.leftLaneDepart, c.hudControl.rightLaneDepart)
    self.frame += 1
    return can_sends

