
#include "esp_wifi.h"

const char* getDisconnectionReasonString(uint8_t reason){
    switch (reason)
    {
    case WIFI_REASON_UNSPECIFIED:
            return "Unspecified";
        case WIFI_REASON_AUTH_EXPIRE:
            return "Authentication expired";
        case WIFI_REASON_AUTH_LEAVE:
            return "Authentication leave. Device left/disconnected after authentication.";
        case WIFI_REASON_ASSOC_EXPIRE:
            return "Association expired.";
        case WIFI_REASON_ASSOC_TOOMANY:
            return "Too many associations.";
        case WIFI_REASON_NOT_AUTHED:
            return "Not authenticated. Incorrect creditentials or settings mismatch.";
        case WIFI_REASON_NOT_ASSOCED:
            return "Not associated with Wifi AP. Denied acsess by AP or failed to find AP.";
        case WIFI_REASON_ASSOC_LEAVE:
            return "Association leave. Intentionally disconnection.";
        case WIFI_REASON_ASSOC_NOT_AUTHED:
            return "Association not authenticated. Incorrect creditentials or settings mismatch.";
        case WIFI_REASON_DISASSOC_PWRCAP_BAD:
            return "Disassociation due to power capability";
        case WIFI_REASON_DISASSOC_SUPCHAN_BAD:
            return "Disassociation due to unsupported channel";
        case WIFI_REASON_BSS_TRANSITION_DISASSOC:
            return "BSS transition disassociation. Connection lost in BSS transition.";
        case WIFI_REASON_IE_INVALID:
            return "Invalid IE in Wifi frame. Error in network config or settings mismatch.";
        case WIFI_REASON_MIC_FAILURE:
            return "MIC failure. Security related issue.";
        case WIFI_REASON_4WAY_HANDSHAKE_TIMEOUT:
            return "4-way handshake timeout. Wrong password.";
        case WIFI_REASON_GROUP_KEY_UPDATE_TIMEOUT:
            return "Group key update timeout.";
        case WIFI_REASON_IE_IN_4WAY_DIFFERS:
            return "IE in 4-way differs from AP.";
        case WIFI_REASON_GROUP_CIPHER_INVALID:
            return "Invalid group cipher";
        case WIFI_REASON_PAIRWISE_CIPHER_INVALID:
            return "Invalid pairwise cipher. Encryption settings mismatch.";
        case WIFI_REASON_AKMP_INVALID:
            return "Invalid AKMP.";
        case WIFI_REASON_UNSUPP_RSN_IE_VERSION:
            return "RSN IE version not supported by AP.";
        case WIFI_REASON_INVALID_RSN_IE_CAP:
            return "Invalid RSN IE capability. Incorrect or invalid RSN IE from STA.";
        case WIFI_REASON_802_1X_AUTH_FAILED:
            return "802.1X authentication failed for the STA.";
        case WIFI_REASON_CIPHER_SUITE_REJECTED:
            return "Cipher suite rejected";
        case WIFI_REASON_TDLS_PEER_UNREACHABLE:
            return "TDLS peer unreachable. Issues with another device.";
        case WIFI_REASON_TDLS_UNSPECIFIED:
            return "TDLS unspecified. Issues with another device.";
        case WIFI_REASON_SSP_REQUESTED_DISASSOC:
            return "STA requested disassociation by SSP.";
        case WIFI_REASON_NO_SSP_ROAMING_AGREEMENT:
            return "No SSP roaming agreement";
        case WIFI_REASON_BAD_CIPHER_OR_AKM:
            return "Bad cipher or AKM. Encryption chiper, or authentication and key management not supported by AP.";
        case WIFI_REASON_NOT_AUTHORIZED_THIS_LOCATION:
            return "Not authorized in this location";
        case WIFI_REASON_SERVICE_CHANGE_PERCLUDES_TS:
            return "Service change precludes TS";
        case WIFI_REASON_UNSPECIFIED_QOS:
            return "Unspecified QoS. Communication is not specified or defined properly.";
        case WIFI_REASON_NOT_ENOUGH_BANDWIDTH:
            return "Not enough bandwidth";
        case WIFI_REASON_MISSING_ACKS:
            return "Missing ACKs";
        case WIFI_REASON_EXCEEDED_TXOP:
            return "Exceeded TXOP";
        case WIFI_REASON_STA_LEAVING:
            return "STA leaving voluntarily, or forrced to by AP.";
        case WIFI_REASON_END_BA:
            return "End BA";
        case WIFI_REASON_UNKNOWN_BA:
            return "Unknown BA";
        case WIFI_REASON_TIMEOUT:
            return "Timeout";
        case WIFI_REASON_PEER_INITIATED:
            return "Peer (another device) initiated disconnection.";
        case WIFI_REASON_AP_INITIATED:
            return "AP initiated disconnection.";
        case WIFI_REASON_INVALID_FT_ACTION_FRAME_COUNT:
            return "Invalid FT action frame count";
        case WIFI_REASON_INVALID_PMKID:
            return "Invalid PMKID";
        case WIFI_REASON_INVALID_MDE:
            return "Invalid MDE";
        case WIFI_REASON_INVALID_FTE:
            return "Invalid FTE";
        case WIFI_REASON_TRANSMISSION_LINK_ESTABLISH_FAILED:
            return "Transmission link establishment failed. Low RSSI or interference.";
        case WIFI_REASON_ALTERATIVE_CHANNEL_OCCUPIED:
            return "Alternative channel occupied.";
        case WIFI_REASON_BEACON_TIMEOUT:
            return "Beacon timeout. Wifi-network issues: Low RSSI, interference or such.";
        case WIFI_REASON_NO_AP_FOUND:
            return "No AP found";
        case WIFI_REASON_AUTH_FAIL:
            return "Authentication failed. Incorrect creditenials or settings mismatch.";
        case WIFI_REASON_ASSOC_FAIL:
            return "Association failed";
        case WIFI_REASON_HANDSHAKE_TIMEOUT:
            return "Handshake timeout. Wrong password.";
        case WIFI_REASON_CONNECTION_FAIL:
            return "Connection failed";
        case WIFI_REASON_AP_TSF_RESET:
            return "AP TSF reset";
        case WIFI_REASON_ROAMING:
            return "Roaming";
        case WIFI_REASON_ASSOC_COMEBACK_TIME_TOO_LONG:
            return "Association comeback time too long";
        case WIFI_REASON_SA_QUERY_TIMEOUT:
            return "SA query timeout";
        default:
            return "Unknown";
    }

}