---
source_id: bulletin-lennox-tsb-2024-001-icomfort
type: markdown
bucket: bulletins
title: "Lennox TSB 2024-001 — iComfort S30 thermostat firmware update"
issuer: Lennox (synthetic)
manufacturer: Lennox
doc_date: 2024-02-20
license: synthetic-internal
---

# Lennox Technical Service Bulletin 2024-001

**Subject:** iComfort S30 thermostat — firmware update for intermittent
Wi-Fi disconnect after extended brownout events.

**Affected models:** 10F81 (iComfort S30 v1.x firmware). Production
dates 2022-06 through 2023-11. Serial range LCS22F-0001 through
LCS23K-9999.

**Severity:** Service — not safety.

## Symptom

Following an extended low-voltage event (brownout > 2 minutes) or
multiple rapid power cycles, the iComfort S30 enters a state where the
Wi-Fi radio remains powered but does not associate with the configured
SSID. The thermostat continues to control the HVAC equipment normally;
the LennoxPros app and remote monitoring become unavailable.

A power cycle of the thermostat alone (by pulling the faceplate from
the wall plate) does not resolve the symptom. A full 24V power cycle
at the breaker resolves the symptom transiently but it recurs on the
next brownout.

## Resolution

Firmware update **v1.18.04** restores correct Wi-Fi radio re-association
behavior after brownout. Update is delivered over the air to any S30
that is currently connected to the cloud; manual update via USB stick
is available for thermostats that have lost cloud connectivity.

Manual update procedure:

1. Download `LCS30_1_18_04.bin` from LennoxPros &rarr; Technical
   Documents &rarr; Firmware.
2. Copy to the root of a FAT32-formatted USB stick.
3. Power down the S30 by pulling the faceplate.
4. Insert USB stick into the rear USB-A port on the wall plate.
5. Reseat the faceplate. The firmware update runs automatically;
   estimated 4 minutes. The screen displays a progress bar.
6. Verify firmware version under Settings &rarr; About after reboot.

## Warranty disposition

This update is **not warranty-replacement eligible** — it is a
firmware-only fix. Replacement under warranty will be denied if the
service tech has not first applied v1.18.04.

## Distributor notes

Stock implications: zero. This is a software fix; no parts movement.
Counter staff should direct any contractor reporting the symptom to
this TSB or to LennoxPros directly.

Related products carrying the iComfort S30 platform: see
[[manufacturers/Lennox]] for the lineup.
