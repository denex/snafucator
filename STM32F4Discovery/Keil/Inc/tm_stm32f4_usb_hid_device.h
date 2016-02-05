/**
 * @author  Tilen Majerle
 * @email   tilen@majerle.eu
 * @website http://stm32f4-discovery.com
 * @link    http://stm32f4-discovery.com/2014/09/library-34-stm32f4-usb-hid-device
 * @version v1.0
 * @ide     Keil uVision
 * @license GNU GPL v3
 * @brief   USB HID Device library for STM32F4
 *	
@verbatim
   ----------------------------------------------------------------------
    Copyright (C) Tilen Majerle, 2015
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.
     
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
   ----------------------------------------------------------------------
@endverbatim
 */
#ifndef TM_USB_HIDDEVICE_H
#define TM_USB_HIDDEVICE_H 100
/**
 * @addtogroup TM_STM32F4xx_Libraries
 * @{
 */

/**
 * @defgroup TM_USB_HID_DEVICE
 * @brief    USB HID Device library for STM32F4xx - http://stm32f4-discovery.com/2014/09/library-34-stm32f4-usb-hid-device
 * @{
 *
 * Library is designed to operate as HID device. This means that STM32F4xx device will be shown to your computer 
 * as USB Keyboard, Mouse and 2 game pads at the same time.
 *
 * It works in USB FS or USB HS in FS mode.
 *
 * By default, library works in USB FS mode (for STM32F4-Discovery board).
 * If you want to use this on STM32F429-Discovery board, you have to activate USB HS in FS mode.
 * Activate this with lines below in your defines.h file:
 *
@verbatim
//Activate USB HS in FS mode
#define USE_USB_OTG_HS
@endverbatim
 *
 * \par Pinout
 *
@verbatim
USB			|STM32F4xx FS mode				|STM32F4xx HS in FS mode	|Notes
			|STM32F4-Discovery				|STM32F429-Discovery

Data +		PA12							PB15						Data+ for USB, standard and used pin
Data -		PA11							PB14						Data- for USB, standard and used pin
ID			PA10							PB12						ID pin, used on F4 and F429 discovery boards, not needed if you don't like it
VBUS		PA9								PB13						VBUS pin, used on F4 and F429 discovery board for activating USB chip.
	
@endverbatim
 *
 * You have to use VBUS on discovery boards, but on nucleo, it's ok with only Data+ and Data- pins
 * Disable necessary pins
 *
 * USB technically needs only Data+ and Data- pins.
 * Also, ID pin can be used, but it is not needed.
 *
 * \par Disable ID PIN
 *
 * If you need pin for something else, where ID is located, you can disable this pin for USB.
 * Add lines below in your defines.h file:
 *
@verbatim
//Disable ID pin
#define USB_HID_HOST_DISABLE_ID
@endverbatim
 *
 * \par Disable VBUS PIN
 *
 * VBUS pin is located on Discovery boards, to activate USB chip on board.
 * If you are working with Discovery boards, then you need this pin, otherise USB will not work.
 * But if you are working on other application (or Nucleo board), you only need Data+ and Data- pins.
 * To disable VBUS pin, add lines below in your defines.h file:
 *
@verbatim
//Disable VBUS pin
#define USB_HID_HOST_DISABLE_VBUS
@endverbatim
 *
 * \par Changelog
 *
@verbatim
 Version 1.0
  - First release
@endverbatim
 *
 * \par Dependencies
 *
@verbatim
 - STM32F4xx
 - STM32F4xx RCC
 - STM32F4xx GPIO
 - STM32F4xx EXTI
 - misc.h
 - defines.h
 - USB HID DEVICE
@endverbatim
 */

#include "stm32f4xx.h"
#include "stm32f4xx_hal_rcc.h"
#include "stm32f4xx_hal_gpio.h"

#include  "usbd_hid.h"
#include  "usbd_desc.h"
 
/**
 * @defgroup TM_USB_HID_DEVICE_Typedefs
 * @brief    Library Typedefs
 * @{
 */

/**
 * @brief  USB HID device enumeration	
 */
typedef enum {
	TM_USB_HIDDEVICE_Status_LibraryNotInitialized = 0x00, /*!< Library is not initialized yet */
	TM_USB_HIDDEVICE_Status_Connected,                    /*!< Device is connected and ready to use */
	TM_USB_HIDDEVICE_Status_Disconnected,                 /*!< Device is not connected */
	TM_USB_HIDDEVICE_Status_IdleMode,                     /*!< Device is is IDLE mode */
	TM_USB_HIDDEVICE_Status_SuspendMode                   /*!< Device is in suspend mode */
} TM_USB_HIDDEVICE_Status_t;

/**
 * @brief  Button status enumeration
 */
typedef enum {
	TM_USB_HIDDEVICE_Button_Released = 0x00, /*!< Button is not pressed */
	TM_USB_HIDDEVICE_Button_Pressed = 0x01   /*!< Button is pressed */
} TM_USB_HIDDEVICE_Button_t;

/**
 * @brief  Keyboard structure
 * @note   Keyboard has special 8 buttons (CTRL, ALT, SHIFT, GUI (or WIN), all are left and right).
 *         It also supports 6 others keys to be pressed at same time, let's say Key1 = 'a', Key2 = 'b', and you will get "ab" result on the screen.
 *         If key is not used, then 0x00 value should be set!
 */
typedef struct {
	TM_USB_HIDDEVICE_Button_t L_CTRL;  /*!< Left CTRL button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t L_ALT;   /*!< Left ALT button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t L_SHIFT; /*!< Left SHIFT button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t L_GUI;   /*!< Left GUI (Win) button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t R_CTRL;  /*!< Right CTRL button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t R_ALT;   /*!< Right ALT button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t R_SHIFT; /*!< Right SHIFT button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	TM_USB_HIDDEVICE_Button_t R_GUI;   /*!< Right GUI (Win) button. This parameter can be a value of @ref TM_USB_HIDDEVICE_Button_t enumeration */
	uint8_t Key1;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
	uint8_t Key2;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
	uint8_t Key3;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
	uint8_t Key4;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
	uint8_t Key5;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
	uint8_t Key6;                      /*!< Key used with keyboard. This can be whatever. Like numbers, letters, everything. */
} TM_USB_HIDDEVICE_Keyboard_t;

/**
 * @brief  Sets default values to work with keyboard
 * @param  *Keyboard_Data: Pointer to empty @ref TM_USB_HIDDEVICE_Keyboard_t structure
 * @retval Member of @ref TM_USB_HIDDEVICE_Status_t enumeration
 */
TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardStructInit(TM_USB_HIDDEVICE_Keyboard_t* Keyboard_Data);

/**
 * @brief  Sends keyboard report over USB
 * @param  *Keyboard_Data: Pointer to @ref TM_USB_HIDDEVICE_Keyboard_t structure to get data from
 * @retval Member of @ref TM_USB_HIDDEVICE_Status_t enumeration
 */
TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardSend(TM_USB_HIDDEVICE_Keyboard_t* Keyboard_Data);

/**
 * @brief  Release all buttons from keyboard
 * @note   If you press a button and don't release it, computer will detect like long pressed button
 * @param  None
 * @retval Member of @ref TM_USB_HIDDEVICE_Status_t enumeration
 */
TM_USB_HIDDEVICE_Status_t TM_USB_HIDDEVICE_KeyboardReleaseAll(void);

/* C++ detection */
#ifdef __cplusplus
}
#endif

#endif
