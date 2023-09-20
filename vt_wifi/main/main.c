#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_netif_ip_addr.h"
#include "esp_mac.h"
#include "inttypes.h"

#include "lwip/ip_addr.h"
#include "lwip/ip4_addr.h"

#include "reasons.c"

#define ESP_WIFI_SSID      "VitalThings" //"SSIKT-Gjest" // "SSIKT-PSK"
#define ESP_WIFI_PASS      "vtSomnofy#18"

static const char *TAG = "VT-ESP-DEV";
int ip_count = 0; //To test if the script reassigns the IP-adress if the ip is invalid
int ip_loss_count = 0; //To test IP-loss

//Scan and obtain information about the AP we wish to connecto to
void scan_ap(const char* target_ssid){
    uint8_t ap_num = 0;
    wifi_ap_record_t *ap_records;

    wifi_scan_config_t scan_config = {
        .ssid = target_ssid,
        .bssid = 0,
        .channel = 0,
        .show_hidden = true,
    };

    printf("**Start scanning\n");
    ESP_ERROR_CHECK(esp_wifi_scan_start(&scan_config,true));

    esp_wifi_scan_get_ap_num(&ap_num);
    printf("\n--------scan count of AP is %d-------\n", ap_num);
    
    ap_records = (wifi_ap_record_t *)malloc(ap_num * sizeof(wifi_ap_record_t));
    ESP_ERROR_CHECK(esp_wifi_scan_get_ap_records(&ap_num, ap_records));

    for(int i = 0; i < ap_num; i++){
            printf("----------------------------------------------------------------\n");
            printf("[%s] [RSSI=%d] [BSSID="MACSTR"] [CHANNEL=%d %d] [AUTHMODE=%d]\n",
                ap_records[i].ssid,
                ap_records[i].rssi,
                MAC2STR(ap_records[i].bssid),
                ap_records[i].primary,
                ap_records[i].second,
                ap_records[i].authmode               
            );
        
    }
    free(ap_records);
    printf("\n**Completed!\n");  
}


static void event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data)
{
    if(event_base == WIFI_EVENT) {
        switch (event_id){
        case WIFI_EVENT_STA_START:
            ESP_LOGI(TAG, "*** WIFI STATION STARTED ***\n");
            esp_wifi_connect();
            break;
            
        case WIFI_EVENT_STA_CONNECTED:
            ESP_LOGI(TAG, "*** WIFI CONNECTED ***\n");
            break;
        
        case WIFI_EVENT_STA_DISCONNECTED:
            ESP_LOGI(TAG, "*** WIFI DISCONNECTED ***\n");

            //Log disconnection reason
            wifi_event_sta_disconnected_t *disconn = (wifi_event_sta_disconnected_t *)event_data;
            ESP_LOGI(TAG, "Disconnection reason: %s\n", getDisconnectionReasonString(disconn->reason));

            scan_ap(ESP_WIFI_SSID); //Set argument to NULL if scan all APs

            if (disconn->reason == WIFI_REASON_ROAMING) {
                printf("Station roaming, do nothing\n");
            } else {
                printf("Try to reconnect to SSID");
                //Add logic such that password can be updated
                esp_wifi_connect();
            }    
            break;
        }
    } else if(event_base == IP_EVENT){
        switch (event_id){
        //If station recives IP4 adress
        case IP_EVENT_STA_GOT_IP:
            ESP_LOGI(TAG,"*** GOT IP ***\n");
            
            ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
            
            //Assign an invalid adress one time  
            while(ip_count < 1){
                event->ip_info.ip.addr = IPADDR_LOOPBACK;;
                ip_count++;
            }
            
            // Check if the IP address is valid
            if (event->ip_info.ip.addr != 0 && event->ip_info.ip.addr != IPADDR_NONE && 
                event->ip_info.ip.addr != IPADDR_ANY && event->ip_info.ip.addr != IPADDR_LOOPBACK &&
                event->ip_info.ip.addr != IPADDR_BROADCAST) {      
                ESP_LOGI(TAG, "Valid IP address obtained.\n"); 

            } else {   
                ESP_LOGI(TAG, "Invalid IP address obtained. Error in network configuration.");
                
                // Reassign IP address by releasing and renewing the DHCP lease
                esp_netif_dhcpc_stop(esp_netif_get_handle_from_ifkey("WIFI_STA_DEF"));
                esp_netif_dhcpc_start(esp_netif_get_handle_from_ifkey("WIFI_STA_DEF")); 
            } 

            //Logging IP, netmask and gateway information
            ESP_LOGI(TAG, "[ip="IPSTR"] [netmask="IPSTR"] [gw="IPSTR"]", 
            IP2STR(&event->ip_info.ip),
            IP2STR(&event->ip_info.netmask),
            IP2STR(&event->ip_info.gw)
            );

            // Get the DNS servers
            esp_netif_dns_info_t gdns1, gdns2, gdns3;
            esp_netif_t *netif = event->esp_netif;
            ESP_ERROR_CHECK(esp_netif_get_dns_info(netif, ESP_NETIF_DNS_MAIN, &gdns1));
            ESP_ERROR_CHECK(esp_netif_get_dns_info(netif, ESP_NETIF_DNS_BACKUP, &gdns2));
            ESP_ERROR_CHECK(esp_netif_get_dns_info(netif, ESP_NETIF_DNS_FALLBACK, &gdns3));

            ESP_LOGI(TAG, "DNS [main="IPSTR"] [backup="IPSTR"] [fallback="IPSTR"]", 
            IP2STR(&gdns1.ip.u_addr.ip4),
            IP2STR(&gdns2.ip.u_addr.ip4),
            IP2STR(&gdns3.ip.u_addr.ip4)  
            );
            break;

        case IP_EVENT_STA_LOST_IP:
            ESP_LOGI(TAG,"*** LOST IP *** \n");
            break;

        default:
            ESP_LOGI(TAG, "Unhandled IP event: %ld", event_id);
            break;
        }

    } else{
        ESP_LOGI(TAG, "******Other event\n");
        // Reconnect to Wi-Fi after a delay
        vTaskDelay(3000 / portTICK_PERIOD_MS);
        esp_wifi_connect();
    }
}


void wifi_init_sta(){
    // Initialize Wi-Fi
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    ESP_ERROR_CHECK(esp_netif_init());

    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));

    // Calling the event handler
    esp_event_handler_instance_t instance_any_id;
    esp_event_handler_instance_t instance_got_ip;
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL,
                                                        &instance_any_id));

    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &event_handler,
                                                        NULL, &instance_got_ip));  

    
    // Connect to AP
     wifi_config_t wifi_sta_config = {
        .sta = {
            .ssid = ESP_WIFI_SSID,
            .password = ESP_WIFI_PASS,
            // .threshold = {
            //     .authmode = WIFI_AUTH_WPA2_PSK, 
            // },
            .scan_method = WIFI_ALL_CHANNEL_SCAN, // WIFI_FAST_SCAN, 
            .sort_method = WIFI_CONNECT_AP_BY_SIGNAL,
        },
    };

    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_sta_config));                                                                                                       

    // Start Wifi
    ESP_ERROR_CHECK(esp_wifi_start());  
    ESP_ERROR_CHECK(esp_wifi_connect()); 

    ESP_LOGI(TAG, "*** WIFI STATION FINISHED ***\n \n");
}

// This is called by ESP32
void app_main()
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    wifi_init_sta();
}



