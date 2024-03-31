using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class ServerScript : MonoBehaviour
{
    TcpClient client = null;
    NetworkStream stream = null;
    Thread thread;
    public TextMeshProUGUI text;

    private void Start()
    {
        thread = new Thread(new ThreadStart(SetupServer));
        thread.Start();
    }

    private void Update()
    {
        // Check if the stream is valid before reading
        if (stream != null && stream.CanRead)
        {
            if (stream.DataAvailable)
            {
                byte[] buffer = new byte[2048];
                int bytesRead = stream.Read(buffer, 0, buffer.Length);
                string data = Encoding.UTF8.GetString(buffer, 0, bytesRead);

                Debug.Log("----------------DATA PAYLOAD--------------------");
                Debug.Log(data);
                Debug.Log("----------------END DATA PAYLOAD---------------");
                
                if (data.Contains("<BEGINNING TRANSCRIPTION TRANSMISSION>")) text.text = "";
                else if (data.Contains("<FLUSH>")) {
                    text.text = data.Replace("<FLUSH>", "");
                } else {
                    text.text += data;
                } // Append data to the text
            }
        }
    }

    private void SetupServer()
    {
        try
        {

            client = new TcpClient("127.0.0.1", 9003);
            stream = client.GetStream();

        }
        catch (SocketException e)
        {
            Debug.Log("SocketException: " + e);
        }
        finally
        {

        }
    }

    private void OnApplicationQuit()
    {
        if (stream != null)
            stream.Close();
        if (client != null)
            client.Close();
        if (thread != null && thread.IsAlive)
            thread.Abort();
    }

}

// public class SocketServer : MonoBehaviour
// {
//     public int port = 9001; // Port number to listen on

//     private TcpListener tcpListener;
//     private TcpClient headset;
//     private NetworkStream stream;
//     private bool isRunning = false;
//     private bool isConnected = false;

//     public TextMeshProUGUI text;

//     void Start()
//     {
//         StartServer();
//     }

//     private void StartServer()
//     {
//         try
//         {
//             // Create a TCP listener on the specified port
//             tcpListener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
//             tcpListener.Start();

//             // Start listening for incoming connections in a separate thread
//             isRunning = true;
//             headset = tcpListener.AcceptTcpClient();
//             stream = headset.GetStream();
//             Debug.Log("Client connected");

//             Debug.Log("Server started on port " + port);
//         }
//         catch (Exception e)
//         {
//             Debug.LogError("Error starting server: " + e.Message);
//         }
//     }

//     void Update() {
//         // Check if the stream is valid before reading
//         if (stream != null && stream.CanRead)
//         {
//             if (stream.DataAvailable)
//             {
//                 byte[] buffer = new byte[2048];
//                 int bytesRead = stream.Read(buffer, 0, buffer.Length);
//                 string data = Encoding.UTF8.GetString(buffer, 0, bytesRead);

//                 if (data.Contains("<FLUSH>")) {
//                     data.Replace("<FLUSH>", "");
//                     text.text = data;
//                 }
//                 else if (data.Contains("<BEGINNING TRANSCRIPTION TRANSMISSION>")) text.text = "";
//                 else {
//                     data.Replace("<FLUSH>", "");
//                     text.text += data;
//                 } // Append data to the text
//             }
//         }
//     }
// }
//     private void HandleClientConnection(object clientObject)
//     {
//         TcpClient client = (TcpClient)clientObject;

//         // Get the network stream for reading/writing data
//         NetworkStream stream = client.GetStream();

//         byte[] buffer = new byte[2048];
//         int bytesRead;

//         try
//         {
//             while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) != 0)
//             {
//                 // Convert the received bytes to a string
//                 string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead);
//                 Debug.Log("Received: " + dataReceived);

//                 if (data.Contains("<FLUSH>")) {
//                     data.Replace("<FLUSH>", "");
//                     text.text = data;
//                 }
//                 else if (data.Contains("<BEGINNING TRANSCRIPTION TRANSMISSION>")) text.text = "";
//                 else {
//                     data.Replace("<FLUSH>", "");
//                     text.text += data;
//                 } // Append data to the text
//             }
//         }
//         catch (Exception e)
//         {
//             Debug.LogError("Error handling client connection: " + e.Message);
//         }
//         finally
//         {
//             // Close the client connection when done
//             client.Close();
//             Debug.Log("Client disconnected");
//         }
//     }
// }