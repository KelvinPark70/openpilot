# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-
from cereal import car, log

# Priority
class Priority:
  LOWEST = 0
  LOW_LOWEST = 1
  LOW = 2
  MID = 3
  HIGH = 4
  HIGHEST = 5

AlertSize = log.ControlsState.AlertSize
AlertStatus = log.ControlsState.AlertStatus
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
VisualAlert = car.CarControl.HUDControl.VisualAlert

class Alert():
  def __init__(self,
               alert_type,
               alert_text_1,
               alert_text_2,
               alert_status,
               alert_size,
               alert_priority,
               visual_alert,
               audible_alert,
               duration_sound,
               duration_hud_alert,
               duration_text,
               alert_rate=0.):

    self.alert_type = alert_type
    self.alert_text_1 = alert_text_1
    self.alert_text_2 = alert_text_2
    self.alert_status = alert_status
    self.alert_size = alert_size
    self.alert_priority = alert_priority
    self.visual_alert = visual_alert
    self.audible_alert = audible_alert

    self.duration_sound = duration_sound
    self.duration_hud_alert = duration_hud_alert
    self.duration_text = duration_text

    self.start_time = 0.
    self.alert_rate = alert_rate

    # typecheck that enums are valid on startup
    tst = car.CarControl.new_message()
    tst.hudControl.visualAlert = self.visual_alert

  def __str__(self):
    return self.alert_text_1 + "/" + self.alert_text_2 + " " + str(self.alert_priority) + "  " + str(
      self.visual_alert) + " " + str(self.audible_alert)

  def __gt__(self, alert2):
    return self.alert_priority > alert2.alert_priority


ALERTS = [
  Alert(
      "turningIndicatorOn",
      "�� �ñ׳� �۵� �� �ڵ��� ����ּ���",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.HIGH, VisualAlert.none, AudibleAlert.none, 0., 0., .1),
  Alert(
      "lkasButtonOff",
      "�������Ϸ� ����� ���� ������ LKAS ��ư�� �����ּ���",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.HIGH, VisualAlert.none, AudibleAlert.none, 0., 0., .1),

  # Miscellaneous alerts
  Alert(
      "enable",
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeEngage, 4., 0., 0.),

  Alert(
      "disable",
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeDisengage, 4., 0., 0.),

  Alert(
      "fcw",
      "�극��ũ!",
      "�ߵ� ����",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.chimeWarningRepeat, 1., 2., 2.),

  Alert(
      "fcwStock",
      "�극��ũ!",
      "�ߵ� ����",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 1., 2., 2.),  # no EON chime for stock FCW

  Alert(
      "steerSaturated",
      "�ڵ��� ����ּ���",
      "��Ƽ� ��ũ�� �����ϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., 2., 3.),

  Alert(
      "steerTempUnavailable",
      "�ڵ��� ����ּ���",
      "������� �Ͻ������� ��Ȱ��ȭ �Ǿ����ϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeWarning1, .4, 2., 3.),

  Alert(
      "steerTempUnavailableMute",
      "�ڵ��� ����ּ���",
      "������� �Ͻ������� ��Ȱ��ȭ �Ǿ����ϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2, .2, .2),

  Alert(
      "preDriverDistracted",
      "���λ�Ȳ�� ���Ǹ� ����̼��� : ���� �길",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "promptDriverDistracted",
      "���λ�Ȳ�� �����ϼ���",
      "���� �길",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeRoadWarning, 4., .1, .1),

  Alert(
      "driverDistracted",
      "���: ������� ��� �����˴ϴ�",
      "���� �길",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "preDriverUnresponsive",
      "�ڵ��� ��ġ�ϼ���: ����͸� ����",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "promptDriverUnresponsive",
      "�ڵ��� ��ġ�ϼ���",
      "������ ����͸� ����",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarning2, .1, .1, .1),

  Alert(
      "driverUnresponsive",
      "���: ������� ��� �����˴ϴ�",
      "������ ����͸� ����",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "driverMonitorLowAcc",
      "������ �� Ȯ�� ��",
      "������ �� �ν��� ��ƽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .4, 0., 1.),

  Alert(
      "geofence",
      "���� �ʿ�",
      "���� �潺 ������ ���� ����",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, .1, .1),

  Alert(
      "startup",
      "�������Ϸ� ����غ� �Ǿ����ϴ�",
      "���������� ���� �׻� �ڵ��� ��� ���α��� ��Ȳ�� �ֽ��ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.chimeReady, 5., 0., 5.),

  Alert(
      "startupMaster",
      "���: �� �귣ġ�� �׽�Ʈ���� �ʾҽ��ϴ�",
      "���������� ���� �׻� �ڵ��� ��� ���α��� ��Ȳ�� �ֽ��ϼ���",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "startupNoControl",
      "��� ���(���ķ ���)",
      "���������� ���� �׻� �ڵ��� ��� ���α��� ��Ȳ�� �ֽ��ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "startupNoCar",
      "��ϸ��(�������� �ʴ� ����)",
      "���������� ���� �׻� �ڵ��� ��� ���α��� ��Ȳ�� �ֽ��ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., 15.),

  Alert(
      "ethicalDilemma",
      "���: �ڵ��� ��� ����ּ���",
      "������ �������� �߰ߵǾ����ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 1., 3., 3.),

  Alert(
      "steerTempUnavailableNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ��� �Ͻ������� ��Ȱ��ȭ �Ǿ����ϴ�.",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "manualRestart",
      "�ڵ��� ����ּ���",
      "�������� ������ �簳�ϼ���",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "resumeRequired",
      "����",
      "����Ϸ��� RES�� ��������",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "belowSteerSpeed",
      "�ڵ��� ����ּ���",
      "�����ӵ��� ���� ������� �Ͻ������� ��Ȱ��ȭ �Ǿ����ϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.none, 0., 0.4, .3),

  Alert(
      "debugAlert",
      "DEBUG ALERT",
      "",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1, .1, .1),
  Alert(
      "preLaneChangeLeft",
      "���� ������ ���� �ڵ��� �������� ��¦ ��������",
      "�ٸ� ������ �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "preLaneChangeRight",
      "���� ������ ���� �ڵ��� �������� ��¦ ��������",
      "�ٸ� ������ �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1, alert_rate=0.75),

  Alert(
      "laneChange",
      "���� ���� ��",
      "�ٸ� ������ �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .0, .1, .1),
  
    Alert(
      "rightLCAbsm",
      "������ ���� ���� ��",
      "���� ������ ���� ��� ����մϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.none, 0., 0.4, .3),
  
  Alert(
      "leftLCAbsm",
      "������ ���� ���� ��",
      "���� ������ ���� ��� ����մϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.none, 0., 0.4, .3),
  
  Alert(
      "preventLCA",
      "�ڵ��� ����ּ���",
      "���� ��Ȳ �Ҿ����� ���������� ��ҵǾ����ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeWarningRepeat, .4, 3., 3.,),


  Alert(
      "posenetInvalid",
      "�ڵ��� ����ּ���",
      "���� ���� �ν��� �Ҿ��մϴ�",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeViewUncertain, 6., 2., 3.),

  # Non-entry only alerts
  Alert(
      "wrongCarModeNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�� ���� ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "dataNeededNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "Ķ���극�̼��� ���� ������ �ʿ�, �ڷḦ ���ε� �Ͻð� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "outOfSpaceNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ������ �����մϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 0., 3.),

  Alert(
      "pedalPressedNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�극��ũ ��� ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, "brakePressed", AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "speedTooLowNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� �ӵ��� �ʹ� �����ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "brakeHoldNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�극��ũ ���� �ʿ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "parkBrakeNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� �극��ũ ���� �ʿ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "lowSpeedLockoutNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "ũ���� ��� ����: �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "lowBatteryNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���͸� ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "sensorDataInvalidNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "EON �����κ��� �����͸� ���� ���߽��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "soundsUnavailableNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ��ġ�� ã�� �� �����ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "tooDistractedNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "������ ���� �길",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  # Cancellation alerts causing soft disabling
  Alert(
      "overheat",
      "�������Ϸ� ��� ���",
      "�ý����� �����Ǿ����ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "wrongGear",
      "�������Ϸ� ��� ���",
      "�� ����̺� ���°� �ƴմϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeGearDrive, 4., 2., 2.),

  Alert(
      "calibrationInvalid",
      "�������Ϸ� ��� ���",
      "Ķ���극�̼� ����: EON�� �� �����ϰ� �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "calibrationIncomplete",
      "�������Ϸ� ��� ���",
      "Ķ���극�̼� ���� ��...",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "doorOpen",
      "�������Ϸ� ��� ���",
      "��� �����ֽ��ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeDoorOpen, .1, 2., 2.),

  Alert(
      "seatbeltNotLatched",
      "�������Ϸ� ��� ���",
      "������Ʈ ��ü��",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeSeatBelt, .1, 2., 2.),

  Alert(
      "espDisabled",
      "�������Ϸ� ��� ���",
      "ESP ����",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "lowBattery",
      "�������Ϸ� ��� ���",
      "���͸� ����",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "commIssue",
      "�������Ϸ� ��� ���",
      "���μ��� �� ��� ������ �ֽ��ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarCommIssue",
      "�������Ϸ� ��� ���",
      "���̴� ��� ������ �ֽ��ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarCanError",
      "�������Ϸ� ��� ���",
      "���̴� ��� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  Alert(
      "radarFault",
      "�������Ϸ� ��� ���",
      "���̴� ��� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),


  Alert(
      "lowMemory",
      "�������Ϸ� ��� ���",
      "�޸� ����: EON�� ����� �ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, .1, 2., 2.),

  # Cancellation alerts causing immediate disabling
  Alert(
      "controlsFailed",
      "�������Ϸ� ��� ���",
      "���� ���� �Ұ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "controlsMismatch",
      "�������Ϸ� ��� ���",
      "���� ���� �Ұ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "canError",
      "�������Ϸ� ��� ���",
      "CAN��� ����: �輱�� Ȯ���ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "steerUnavailable",
      "�������Ϸ� ��� ���",
      "LKAS ����: ������ �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "brakeUnavailable",
      "�������Ϸ� ��� ���",
      "ũ���� �ý��� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "gasUnavailable",
      "�������Ϸ� ��� ���",
      "������� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "reverseGear",
      "�������Ϸ� ��� ���",
      "�� �������¿� �ֽ��ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "cruiseDisabled",
      "�������Ϸ� ��� ���",
      "ũ���� ��� ����",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  Alert(
      "plannerError",
      "�������Ϸ� ��� ���",
      "���� ó���� ������ �ֽ��ϴ�",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.steerRequired, AudibleAlert.chimeWarningRepeat, 2.2, 3., 4.),

  # not loud cancellations (user is in control)
  Alert(
      "noTarget",
      "�������Ϸ� ��� �Ұ�",
      "���� ������ �������� �ʾҽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "speedTooLow",
      "�������Ϸ� ��� �Ұ�",
      "���� �ӵ��� �ʹ� �����ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  # Cancellation alerts causing non-entry
  Alert(
      "overheatNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�ý����� �����Ǿ����ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "wrongGearNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�� ����̺� ���°� �ƴմϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeGearDrive, 4., 2., 3.),

  Alert(
      "calibrationInvalidNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "Ķ���극�̼� ����: EON�� �� �����ϰ� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "calibrationIncompleteNoEntry",
      "�������Ϸ� ��� �Ͻ� �Ұ�",
      "Ķ���극�̼� ���� ��...",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "doorOpenNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "��� �����ֽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDoorOpen, 3., 2., 3.),

  Alert(
      "seatbeltNotLatchedNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "������Ʈ�� ü�� �ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeSeatBelt, 4., 2., 3.),

  Alert(
      "espDisabledNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "ESP ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "geofenceNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� �潺 ������ ���� ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.MID, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "radarCanErrorNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���̴� ��� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "radarFaultNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���̴� ��� ����: ���� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "posenetInvalidNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ���� �ν��� �Ҿ��մϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "controlsFailedNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ���� �Ұ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "canErrorNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "CAN��� ����: �輱�� �ٽ� Ȯ���ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "steerUnavailableNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "LKAS ����: ������ �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "brakeUnavailableNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "ũ���� �ý��� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "gasUnavailableNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "������� ����: ������ �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "reverseGearNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�� �������¿� �ֽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "cruiseDisabledNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "ũ���� ��� ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "noTargetNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ������ �������� �ʾҽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "plannerErrorNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���� ó���� ������ �ֽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeError, .4, 2., 3.),

  Alert(
      "commIssueNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���μ��� �� ��� ������ �ֽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "radarCommIssueNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���̴� ��� ������ �ֽ��ϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "internetConnectivityNeededNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "���ͳݿ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  Alert(
      "lowMemoryNoEntry",
      "�������Ϸ� ��� �Ұ�",
      "�޸� ����: EON�� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.chimeDisengage, .4, 2., 3.),

  # permanent alerts
  Alert(
      "steerUnavailablePermanent",
      "LKAS ����: ������ �ٽ� �����ϼ���",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "brakeUnavailablePermanent",
      "ũ���� �ý��� ����: ������ �ٽ� �����ϼ���",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "lowSpeedLockoutPermanent",
      "ũ���� �ý��� ����: ������ �ٽ� �����ϼ���",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "calibrationIncompletePermanent",
      "Ķ���극�̼� ���� ��: ",
      "������ �ӵ��� ���̼��� > ",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "invalidGiraffeToyotaPermanent",
      "�������� �ʴ� ������ ����",
      "comma.ai/tg ����",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "internetConnectivityNeededPermanent",
      "���ͳݿ� �����ϼ���",
      "Ȱ��ȭ�� ���� ������Ʈ�� Ȯ���ؾ� �մϴ�",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "communityFeatureDisallowedPermanent",
      "Ŀ�´�Ƽ ��� ����",
      "Enable Community Features in Developer Settings",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 0., 0., .2),  # LOW priority to overcome Cruise Error

  Alert(
      "sensorDataInvalidPermanent",
      "EON �����κ��� �����͸� ���� ���߽��ϴ�",
      "EON�� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "soundsUnavailablePermanent",
      "���� ��ġ�� ã�� �� �����ϴ�",
      "EON�� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "lowMemoryPermanent",
      "�޸� ���� �ɰ�",
      "EON�� �ٽ� �����ϼ���",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "carUnrecognizedPermanent",
      "��� ���",
      "�νĵ��� ���� ���� ��",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOW_LOWEST, VisualAlert.none, AudibleAlert.none, 0., 0., .2),

  Alert(
      "vehicleModelInvalid",
      "���� �Ű����� �ν� ����",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWEST, VisualAlert.steerRequired, AudibleAlert.none, .0, .0, .1),

  # offroad alerts
  Alert(
      "ldwPermanent",
      "�ڵ��� ����ּ���",
      "���� ��Ż ����",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.chimeLaneDeparture, 5., 2., 3.),
]
