using UnityEngine;
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using UnityEngine.UI;
using System.Threading;
using System.Threading.Tasks;
using Windows.Networking;
using Windows.Networking.Sockets;
using Windows.Networking.Connectivity;
using Windows.Storage.Streams;
using TMPro;
// UNSURE IF WE NEED MORE IMPORTS / IF ANY OF THE IMPORTS ARE UNNECESSARY

/*
    TRANSCRIPTION COMMUNICATION PROTOCOL
    <P> -- means that the last phrase has ended (i.e. a new phrase of text will begin now) -- one phrase is a transcription of someone talking without pause. In between these tags, each "line" sent is the newest update to the current phrase transcription

    <INTEGER> -- the length of the phrase string within the payload that is sent

    Example:
    "Hi my name is Ari and I'm 23 years old. [PAUSE] Right now I'm working with Joey on figuring out how to set up a server listener thingy on Hololens."

    <P><13>Hi my name is...

    <18>Hi my name is Ari.

    <39>Hi my name is Ari and I'm 23 years old.

    <P><12>Right now...

    Etc.
*/

public class TranscriptionReceiver : MonoBehaviour
{
    string port = "9000";
    public TextMeshProUGUI text;
    // string phrase; uncomment this if necessary (see line 102)
    StreamSocketListener listener;
    
    void Start()
    {
        listener = new StreamSocketListener();
        listener.ConnectionReceived += _receiver_socket_ConnectionReceived;

        listener.Control.KeepAlive = true; // May want to change this

        Listener_Start();
    }

    private async void Listener_Start()
    {
        try
        {
            await listener.BindServiceNameAsync(port);
            Debug.Log("Listening on port " + port);
        }
        catch (Exception e)
        {
            Debug.Log("Error: " + e.Message);
        }

       
    }

    private async void _receiver_socket_ConnectionReceived(StreamSocketListener sender, StreamSocketListenerConnectionReceivedEventArgs args)
    {
        string phraseLength;
        try
        {
            while(true)
            {
                using (var dr = new DataReader(args.Socket.InputStream))
                {   
                    phraseLength = "";
                    dr.InputStreamOptions = InputStreamOptions.Partial;
                    dataReader.UnicodeEncoding = Windows.Storage.Streams.UnicodeEncoding.Utf8;
                    await dr.LoadAsync(2048*8); //loading the buffer (probably don't need this large of size)
                    
                    byte b = dr.ReadByte(); // first byte should always be a '<'
                    char c = Convert.toChar(dr.ReadByte()); // if the second byte is a 'P' (for Phrase) we will flush the output. Can do something else in future if we want to change this.
                    if (c == 'P') {
                        // P processing here if we want to do something else. Current behavior is to only display the current phrase being sent (i.e. previous phrases get erased off screen)
                        b = dr.ReadByte() // '>'
                        b = dr.ReadByte() // '<'
                    } 

                    do {
                        phraseLength += c;
                        c = Convert.toChar(dr.ReadByte());
                    } while (c != '>');


                    text = dr.ReadString(Convert.ToInt32(phraseLength)); // IF THIS DOESN'T WORK UNCOMMENT LINES AND COMMENT THESE OUT
                    Debug.Log(text); // IF THIS DOESN'T WORK UNCOMMENT LINES AND COMMENT THESE OUT

                    // phrase = dr.ReadString(Convert.ToInt32(phraseLength)); uncomment this if necessary (see line 97)
                    // Debug.Log(phrase); uncomment this if necessary (see line 97)

                }
            }
        }
        catch (Exception e)
        {
            Debug.log(e.message());
        }
    }

    // void Update() { uncomment this if necessary (see line 97)
    //     text = phrase;
    // }

}
