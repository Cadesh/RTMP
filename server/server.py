import asyncio  
import logging  
import os  
import tempfile 
import time
import subprocess as sp

from pyrtmp import StreamClosedException, RTMPProtocol  
from pyrtmp.messages import SessionManager  
from pyrtmp.messages.audio import AudioMessage  
from pyrtmp.messages.command import NCConnect, NCCreateStream, NSPublish, NSCloseStream, NSDeleteStream  
from pyrtmp.messages.data import MetaDataMessage  
from pyrtmp.messages.protocolcontrol import WindowAcknowledgementSize, SetChunkSize, SetPeerBandwidth  
from pyrtmp.messages.usercontrol import StreamBegin  
from pyrtmp.messages.video import VideoMessage  
from pyrtmp.misc.flvdump import FLVFile, FLVMediaType  
  
logging.basicConfig(level=logging.DEBUG)  
logger = logging.getLogger(__name__)  
logger.setLevel(logging.DEBUG)  

PORT=1942

audio = [] # stores the arriving audio files 
video = [] # stores the arriving video files

#-----------------------------------------------------------------
def storeOutput(payload, format):
    # 1. open outputfile
    output_file = open("output." + format , 'wb')

    # 2. save payloads to file
    for frag in payload:
        output_file.write(frag)

    output_file.close()
    time.sleep(2.0)

    sp.call('ffmpeg -i output.raw video.mp4') 
#-----------------------------------------------------------------


async def simple_controller(reader, writer):  
    session = SessionManager(reader=reader, writer=writer)  
    flv = None  
    try:  
        logger.debug(f'Client connected {session.peername}')  
  
        # do handshake  
        await session.handshake()  
  
        # read chunks  
        async for chunk in session.read_chunks_from_stream():
            message = chunk.as_message()  
            logger.debug(f"Receiving {str(message)} {message.chunk_id}")  
            if isinstance(message, NCConnect):  
                session.write_chunk_to_stream(WindowAcknowledgementSize(ack_window_size=5000000))  
                session.write_chunk_to_stream(SetPeerBandwidth(ack_window_size=5000000, limit_type=2))  
                session.write_chunk_to_stream(StreamBegin(stream_id=0))  
                session.write_chunk_to_stream(SetChunkSize(chunk_size=8192))  
                session.writer_chunk_size = 8192  
                session.write_chunk_to_stream(message.create_response())  
                await session.drain()  
                logger.debug("Response to NCConnect")  
            elif isinstance(message, WindowAcknowledgementSize):  
                pass  
            elif isinstance(message, NCCreateStream):  
                session.write_chunk_to_stream(message.create_response())  
                await session.drain()  
                logger.debug("Response to NCCreateStream")  
            elif isinstance(message, NSPublish):  
                # create flv file at temp  
                flv = FLVFile(os.path.join('./', message.publishing_name))  
                #flv = FLVFile(os.path.join(tempfile.gettempdir(), message.publishing_name))  
                session.write_chunk_to_stream(StreamBegin(stream_id=1))  
                session.write_chunk_to_stream(message.create_response())  
                await session.drain()  
                logger.debug("Response to NSPublish")  
            elif isinstance(message, MetaDataMessage):  
                # Write meta data to file  
                flv.write(0, message.to_raw_meta(), FLVMediaType.OBJECT)  
            elif isinstance(message, SetChunkSize):  
                session.reader_chunk_size = message.chunk_size  
            elif isinstance(message, VideoMessage):  
                # Write video data to file  
                flv.write(message.timestamp, message.payload, FLVMediaType.VIDEO) 
                video.append(message.payload) 
            elif isinstance(message, AudioMessage):  
                # Write data data to file
                flv.write(message.timestamp, message.payload, FLVMediaType.AUDIO)  
                audio.append(message.payload)
            elif isinstance(message, NSCloseStream):  
                pass  
            elif isinstance(message, NSDeleteStream):  
                pass  
            else:  
                logger.debug(f"Unknown message {str(message)}")  
  
    except StreamClosedException as ex:  
        logger.debug(f"Client {session.peername} disconnected!")  
        #storeOutput(audio, 'pcm')
        #storeOutput(video, 'raw')

    finally:  
        if flv:  
            print("Saving FLV file.")
            flv.close()  
  
  
async def serve_rtmp(use_protocol=True):  
    loop = asyncio.get_running_loop()  
    if use_protocol is True:  
        server = await loop.create_server(lambda: RTMPProtocol(controller=simple_controller, loop=loop), '0.0.0.0', PORT)  
    else:  
        server = await asyncio.start_server(simple_controller, '0.0.0.0', PORT)  
    addr = server.sockets[0].getsockname()  
    logger.info(f'Serving on {addr}')  
    async with server:  
        await server.serve_forever()  
  
def wrapper(port: int):
    #asyncio.run(serve_rtmp(port=port))
    asyncio.run(serve_rtmp())

    
IS_DEBUG=True
NUM_PROCESS=2

if __name__ == "__main__":
    if IS_DEBUG is True:
        wrapper(PORT)
    else:
        from multiprocessing import Process
        import uvloop
        uvloop.install()
        process = []
        for i in range(NUM_PROCESS):
            p = Process(target=wrapper, args=(PORT + i + 5,))
            p.start()
            process.append(p)
        for p in process:
            p.join()