#include "msp.h"
#include <stdio.h>
#include <driverlib.h>
#include "uart.h"
#include "string.h"
#include <stdlib.h>
#define dco_freq 3E+6

volatile char receivedBuffer[1] = "";
volatile uint8_t printPrompt = 0;
volatile uint8_t printError = 0;
volatile int i;
volatile char c[200];
volatile int indx;

const eUSCI_UART_Config UART_config =
{
 EUSCI_A_UART_CLOCKSOURCE_SMCLK, // SMCLK Clock Source
 19,
 8,
 85,
 EUSCI_A_UART_NO_PARITY, // No Parity
 EUSCI_A_UART_LSB_FIRST, // LSB First
 EUSCI_A_UART_ONE_STOP_BIT, // One stop bit
 EUSCI_A_UART_MODE, // UART mode
 EUSCI_A_UART_OVERSAMPLING_BAUDRATE_GENERATION
};

void Transmit_EndLine() {
    while ((UCA0IFG & 0x02) == 0) {};
    UART_transmitData(EUSCI_A0_BASE, 0x0D);
    while ((UCA0IFG & 0x02) == 0) {};
    UART_transmitData(EUSCI_A0_BASE, 0x0A);

}

void Clear_c() {
    for (i = 0; i < 200; i++) {
        c[i] = '\x00';
    }
    i = 0;
}

void Transmit_Data() {

    int value = atoi(c);
    printf("%i\n", value);

    while ((UCA0IFG & 0x02) == 0) {};
    for (indx = 0; indx < i; indx++) {
        UART_transmitData(EUSCI_A0_BASE, c[indx]);
    }
    Clear_c();
    Transmit_EndLine();
}

void Transmit_Error() {
    char msg[] = "ERROR: Character Limit Exceeded!";
    while ((UCA0IFG & 0x02) == 0) {};
    int errorIndx = 0;
    for (errorIndx = 0; errorIndx < strlen(msg); errorIndx++) {
        UART_transmitData(EUSCI_A0_BASE, msg[errorIndx]);
    }
    Clear_c();
    Transmit_EndLine();
}

void EUSCIA0_IRQHandler(void) {
    receivedBuffer[0] = EUSCI_A_UART_receiveData(EUSCI_A0_BASE);

    if (receivedBuffer[0] == 0x0D) {
        printPrompt = 1;
    } else {
        c[i] = receivedBuffer[0];
        i++;
        if (i == 200) {
            printError = 1;
        }
    }
}
/**
 * main.c
 */
void main(void)
{
    WDT_A_holdTimer();

    unsigned int dcoFrequency = 3E+6;
    CS_setDCOFrequency(dcoFrequency);
    CS_initClockSignal(CS_SMCLK, CS_DCOCLK_SELECT, CS_CLOCK_DIVIDER_1);

    Interrupt_disableMaster();

    GPIO_setAsPeripheralModuleFunctionInputPin(GPIO_PORT_P1,
                                               GPIO_PIN2,
                                               GPIO_PRIMARY_MODULE_FUNCTION);
    GPIO_setAsPeripheralModuleFunctionOutputPin(GPIO_PORT_P1,
                                                GPIO_PIN3,
                                                GPIO_PRIMARY_MODULE_FUNCTION);

    UART_initModule(EUSCI_A0_BASE, &UART_config);
    UART_enableModule(EUSCI_A0_BASE);


    Interrupt_setPriority(INT_EUSCIA0, 0);
    Interrupt_enableInterrupt(INT_EUSCIA0);

    UART_enableInterrupt(EUSCI_A0_BASE, EUSCI_A_UART_RECEIVE_INTERRUPT);

    Interrupt_enableMaster();

    while (true) {
        if (printPrompt && !printError) {
            Transmit_Data();
            printPrompt = 0;
        }
        if (printError) {
            Transmit_Error();
            printError = 0;
        }
    }

}
