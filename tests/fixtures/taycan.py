GET = {
    "https://api.porsche.com/core/api/v3/se/sv_SE/vehicles": [
        {
            "vin": "WPTAYCAN",
            "isPcc": True,
            "relationship": "OWNER",
            "maxSecondaryUsers": 5,
            "modelDescription": "Taycan Turbo S",
            "modelType": "Y1AFH1",
            "modelYear": "2021",
            "exteriorColor": "Ice Grey Metallic/Ice Grey Metallic",
            "exteriorColorHex": "#2d1746",
            "spinEnabled": True,
            "loginMethod": "PORSCHE_ID",
            "pictures": [],
            "attributes": [],
            "validFrom": "2021-01-15T15:38:03.000Z",
        }
    ],
    "https://api.porsche.com/service-vehicle/vehicle-summary/WPTAYCAN": {
        "modelDescription": "Taycan Turbo S",
        "nickName": None,
    },
    "https://api.porsche.com/service-vehicle/vcs/capabilities/WPTAYCAN": {
        "displayParkingBrake": True,
        "needsSPIN": True,
        "hasRDK": True,
        "engineType": "BEV",
        "carModel": "J1",
        "onlineRemoteUpdateStatus": {"editableByUser": True, "active": True},
        "heatingCapabilities": {
            "frontSeatHeatingAvailable": True,
            "rearSeatHeatingAvailable": True,
        },
        "steeringWheelPosition": "LEFT",
        "hasHonkAndFlash": True,
    },
    "https://api.porsche.com/service-vehicle/car-finder/WPTAYCAN/position": {
        "carCoordinate": {
            "geoCoordinateSystem": "WGS84",
            "latitude": 63.883564,
            "longitude": 12.884809,
        },
        "heading": 273,
    },
    "https://api.porsche.com/e-mobility/de/de_DE/J1/WPTAYCAN?timezone=Europe/Stockholm": {
        "batteryChargeStatus": {
            "plugState": "DISCONNECTED",
            "lockState": "UNLOCKED",
            "chargingState": "OFF",
            "chargingReason": "INVALID",
            "externalPowerSupplyState": "UNAVAILABLE",
            "ledColor": "NONE",
            "ledState": "OFF",
            "chargingMode": "OFF",
            "stateOfChargeInPercentage": 96,
            "remainingChargeTimeUntil100PercentInMinutes": None,
            "remainingERange": {
                "value": 348,
                "unit": "KILOMETER",
                "originalValue": 348,
                "originalUnit": "KILOMETER",
                "valueInKilometers": 348,
                "unitTranslationKey": "GRAY_SLICE_UNIT_KILOMETER",
            },
            "remainingCRange": None,
            "chargingTargetDateTime": "2021-11-12T15:35",
            "status": None,
            "chargeRate": {
                "value": 0,
                "unit": "KM_PER_MIN",
                "valueInKmPerHour": 0,
                "unitTranslationKey": "EM.COMMON.UNIT.KM_PER_MIN",
            },
            "chargingPower": 0,
            "chargingTargetDateTimeOplEnforced": None,
            "chargingInDCMode": False,
        },
        "directCharge": {"disabled": True, "isActive": False},
        "directClimatisation": {
            "climatisationState": "OFF",
            "remainingClimatisationTime": None,
        },
        "chargingStatus": "NOT_CHARGING",
        "timers": [
            {
                "timerID": "1",
                "departureDateTime": "2021-11-17T21:18:00.000Z",
                "preferredChargingTimeEnabled": False,
                "preferredChargingStartTime": None,
                "preferredChargingEndTime": None,
                "frequency": "SINGLE",
                "climatised": True,
                "weekDays": None,
                "active": False,
                "chargeOption": True,
                "targetChargeLevel": 85,
                "e3_CLIMATISATION_TIMER_ID": "4",
                "climatisationTimer": False,
            }
        ],
        "climateTimer": None,
        "chargingProfiles": {
            "currentProfileId": 0,
            "profiles": [
                {
                    "profileId": 4,
                    "profileName": "Allgemein",
                    "profileActive": False,
                    "chargingOptions": {
                        "minimumChargeLevel": 25,
                        "smartChargingEnabled": True,
                        "preferredChargingEnabled": False,
                        "preferredChargingTimeStart": "00:00",
                        "preferredChargingTimeEnd": "06:00",
                    },
                    "position": {"latitude": 0, "longitude": 0},
                }
            ],
        },
        "errorInfo": [],
    },
    "https://api.porsche.com/service-vehicle/se/sv_SE/vehicle-data/WPTAYCAN/stored": {
        "vin": "WPTAYCAN",
        "oilLevel": None,
        "fuelLevel": None,
        "batteryLevel": {
            "value": 96,
            "unit": "PERCENT",
            "unitTranslationKey": "GRAY_SLICE_UNIT_PERCENT",
        },
        "remainingRanges": {
            "conventionalRange": {
                "distance": None,
                "engineType": "UNSUPPORTED",
                "isPrimary": False,
            },
            "electricalRange": {
                "distance": {
                    "value": 348,
                    "unit": "KILOMETER",
                    "originalValue": 348,
                    "originalUnit": "KILOMETER",
                    "valueInKilometers": 348,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_KILOMETER",
                },
                "engineType": "ELECTRIC",
                "isPrimary": True,
            },
        },
        "mileage": {
            "value": 13247,
            "unit": "KILOMETER",
            "originalValue": 13247,
            "originalUnit": "KILOMETER",
            "valueInKilometers": 13247,
            "unitTranslationKey": "GRAY_SLICE_UNIT_KILOMETER",
        },
        "parkingLight": "OFF",
        "parkingLightStatus": None,
        "parkingBreak": "ACTIVE",
        "parkingBreakStatus": None,
        "doors": {
            "frontLeft": "CLOSED_LOCKED",
            "frontRight": "CLOSED_LOCKED",
            "backLeft": "CLOSED_LOCKED",
            "backRight": "CLOSED_LOCKED",
            "frontTrunk": "CLOSED_UNLOCKED",
            "backTrunk": "CLOSED_LOCKED",
            "overallLockStatus": "CLOSED_LOCKED",
        },
        "serviceIntervals": {
            "oilService": {"distance": None, "time": None},
            "inspection": {
                "distance": {
                    "value": -16800,
                    "unit": "KILOMETER",
                    "originalValue": -16800,
                    "originalUnit": "KILOMETER",
                    "valueInKilometers": -16800,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_KILOMETER",
                },
                "time": {
                    "value": -415,
                    "unit": "DAYS",
                    "unitTranslationKey": "GRAY_SLICE_UNIT_DAY",
                },
            },
        },
        "tires": {
            "frontLeft": {
                "currentPressure": {
                    "value": 3,
                    "unit": "BAR",
                    "valueInBar": 3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "optimalPressure": {
                    "value": 3.3,
                    "unit": "BAR",
                    "valueInBar": 3.3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "differencePressure": {
                    "value": 0.3,
                    "unit": "BAR",
                    "valueInBar": 0.3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "tirePressureDifferenceStatus": "DIVERGENT",
            },
            "frontRight": {
                "currentPressure": {
                    "value": 3,
                    "unit": "BAR",
                    "valueInBar": 3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "optimalPressure": {
                    "value": 3.3,
                    "unit": "BAR",
                    "valueInBar": 3.3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "differencePressure": {
                    "value": 0.3,
                    "unit": "BAR",
                    "valueInBar": 0.3,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "tirePressureDifferenceStatus": "DIVERGENT",
            },
            "backLeft": {
                "currentPressure": {
                    "value": 3.2,
                    "unit": "BAR",
                    "valueInBar": 3.2,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "optimalPressure": {
                    "value": 3.8,
                    "unit": "BAR",
                    "valueInBar": 3.8,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "differencePressure": {
                    "value": 0.6,
                    "unit": "BAR",
                    "valueInBar": 0.6,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "tirePressureDifferenceStatus": "DIVERGENT",
            },
            "backRight": {
                "currentPressure": {
                    "value": 3.2,
                    "unit": "BAR",
                    "valueInBar": 3.2,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "optimalPressure": {
                    "value": 3.8,
                    "unit": "BAR",
                    "valueInBar": 3.8,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "differencePressure": {
                    "value": 0.6,
                    "unit": "BAR",
                    "valueInBar": 0.6,
                    "unitTranslationKey": "GRAY_SLICE_UNIT_BAR",
                },
                "tirePressureDifferenceStatus": "DIVERGENT",
            },
        },
        "windows": {
            "frontLeft": "CLOSED",
            "frontRight": "CLOSED",
            "backLeft": "CLOSED",
            "backRight": "CLOSED",
            "roof": "UNSUPPORTED",
            "maintenanceHatch": "UNSUPPORTED",
            "sunroof": {"status": "UNSUPPORTED", "positionInPercent": None},
        },
        "parkingTime": "16.11.2021 14:17:03",
        "overallOpenStatus": "CLOSED",
    },
}