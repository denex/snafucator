/**	
 * |----------------------------------------------------------------------
 * | Copyright (C) Tilen Majerle, 2014
 * | 
 * | This program is free software: you can redistribute it and/or modify
 * | it under the terms of the GNU General Public License as published by
 * | the Free Software Foundation, either version 3 of the License, or
 * | any later version.
 * |  
 * | This program is distributed in the hope that it will be useful,
 * | but WITHOUT ANY WARRANTY; without even the implied warranty of
 * | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * | GNU General Public License for more details.
 * | 
 * | You should have received a copy of the GNU General Public License
 * | along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * |----------------------------------------------------------------------
 */
#include "tm_stm32f4_usb_hid_device.h"
#include "usb_device.h"

/* Keyboard */
TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardStructInit(TM_USB_HIDDEVICE_Keyboard_t* Keyboard_Data) {
	/* Set defaults */
	Keyboard_Data->L_CTRL = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->L_ALT = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->L_SHIFT = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->L_GUI = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->R_CTRL = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->R_ALT = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->R_SHIFT = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->R_GUI = TM_USB_HIDDEVICE_Button_Released;
	Keyboard_Data->Key1 = 0;
	Keyboard_Data->Key2 = 0;
	Keyboard_Data->Key3 = 0;
	Keyboard_Data->Key4 = 0;
	Keyboard_Data->Key5 = 0;
	Keyboard_Data->Key6 = 0;
	
	/* Return currect status */
	return TM_USB_HIDDEVICE_Status_Connected;
}

TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardSend(TM_USB_HIDDEVICE_Keyboard_t* Keyboard_Data) {
	uint8_t buff[8] = {0, 0, 0, 0, 0, 0, 0, 0}; /* 8 bytes long report */
	
	/* Report ID */
	//buff[0] = 0x01; /* Keyboard */
	
	/* Control buttons */
	buff[0] = 0;
	buff[0] |= Keyboard_Data->L_CTRL 	<< 0;	/* Bit 0 */
	buff[0] |= Keyboard_Data->L_SHIFT << 1;	/* Bit 1 */
	buff[0] |= Keyboard_Data->L_ALT 	<< 2;	/* Bit 2 */
	buff[0] |= Keyboard_Data->L_GUI 	<< 3;	/* Bit 3 */
	buff[0] |= Keyboard_Data->R_CTRL 	<< 4;	/* Bit 4 */
	buff[0] |= Keyboard_Data->R_SHIFT << 5;	/* Bit 5 */
	buff[0] |= Keyboard_Data->R_ALT 	<< 6;	/* Bit 6 */
	buff[0] |= Keyboard_Data->R_GUI 	<< 7;	/* Bit 7 */
	
	/* Padding */
	buff[1] = 0x00;
	
	/* Keys */
	buff[2] = Keyboard_Data->Key1;
	buff[3] = Keyboard_Data->Key2;
	buff[4] = Keyboard_Data->Key3;
	buff[5] = Keyboard_Data->Key4;
	buff[6] = Keyboard_Data->Key5;
	buff[7] = Keyboard_Data->Key6;
	
	/* Send to USB */
	USBD_HID_SendReport(&hUsbDeviceFS, buff, sizeof(buff));
	
	/* Return connected */
	return TM_USB_HIDDEVICE_Status_Connected;	
}

TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardReleaseAll(void) {
	uint8_t buff[8] = {0, 0, 0, 0, 0, 0, 0, 0}; /* 8 bytes long report */
	
	/* Report ID */
	//buff[0] = 0x01; /* Keyboard */
	
	/* Send to USB */
	USBD_HID_SendReport(&hUsbDeviceFS, buff, sizeof(buff));
	
	/* Return connected */
	return TM_USB_HIDDEVICE_Status_Connected;
}
