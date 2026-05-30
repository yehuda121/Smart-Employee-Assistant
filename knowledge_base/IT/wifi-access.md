# Corporate WiFi Access

## Purpose

This document explains how Amdocs employees and approved guests connect to wireless networks at Amdocs office locations. Proper WiFi configuration ensures secure connectivity, network segmentation, and compliance with Amdocs information security standards.

## Scope

This procedure covers WiFi access at all Amdocs-owned and leased office facilities globally, including the Ra'anana headquarters, St. Louis campus, Pune development center, Manila operations hub, and Dublin regional office. It applies to corporate-managed devices and personally owned devices (BYOD) used for Amdocs work.

## Procedure

1. **Identify the correct network.** Amdocs offices broadcast the following SSIDs:
   - **Amdocs-Corp:** Primary employee network (802.1X, certificate-based authentication)
   - **Amdocs-Guest:** Visitor network (captive portal, 24-hour sessions)
   - **Amdocs-IoT:** Smart office devices only (not for employee use)

2. **Connect corporate-managed devices (automatic).** Devices enrolled in Intune or Jamf automatically receive the Amdocs-Corp WiFi profile via MDM. Upon entering an Amdocs office, your device should connect without manual configuration. If it does not, run **Sync** in Company Portal (Windows) or check in with Jamf (Mac).

3. **Connect BYOD devices manually.** On personally owned devices, navigate to WiFi settings and select **Amdocs-Corp**. When prompted for credentials, enter your Amdocs email and network password. Accept the Amdocs Root CA certificate when prompted. If certificate installation fails, download the WiFi profile from `https://wifi.amdocs.internal`.

4. **Register guest access.** For visitors, the sponsoring employee must pre-register guests in the **Amdocs Visitor Portal** (`https://visitors.amdocs.internal`) at least 2 hours before arrival. Guests receive a WiFi voucher code via SMS or email. On-site self-registration kiosks are available in lobby areas.

5. **Connect to Amdocs-Guest (visitors).** Select the **Amdocs-Guest** SSID, open a browser, and enter the voucher code. Guest sessions expire after 24 hours and provide internet access only (no internal resource access).

6. **Troubleshoot connectivity issues.** If you cannot connect to Amdocs-Corp:
   - Verify your device is MDM-enrolled and compliant
   - Forget the network and reconnect
   - Move closer to an access point (look for AP labels on ceiling units)
   - Submit a ServiceNow ticket under **Network > WiFi Connectivity**

7. **Report rogue access points.** If you detect an unrecognized SSID resembling Amdocs networks (e.g., "Amdocs-Free"), report it immediately to security@amdocs.com and do not connect.

## Important Notes

- Amdocs-Corp WiFi requires device compliance (encrypted disk, updated OS, active endpoint protection). Non-compliant devices are placed on a remediation VLAN with limited access.
- Bandwidth on Amdocs-Guest is limited to 10 Mbps per device.
- Do not share your WiFi credentials or guest voucher codes. Each employee authentication is individually logged.
- VPN is still required to access internal applications even when connected to Amdocs-Corp WiFi in most regions (exception: Ra'anana HQ uses direct routing for select internal apps).
- WiFi passwords are not used on Amdocs-Corp; authentication is certificate and credential-based via RADIUS.

## Contact Information

- **Network Support:** network-support@amdocs.com | Internal ext. 4720
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357
- **Visitor Registration Help:** visitors@amdocs.com
