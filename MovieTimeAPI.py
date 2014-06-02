#imports for flask framework and command line manipulation                                                                        
from flask import *                                                                                                               
import subprocess                                                                                                                 
import signal                                                                                                                     
import os                                                                                                                         
import fnmatch                                                                                                                    
import glob                                                                                                                       
                                                                                                                                  
app=Flask(__name__) #constructing app a new Flask Object                                                                          
app.config['MOVIE_PROCESSOR'] = None #initializing what will be a movie processor instance field in the app's config lis          
app.config['CURRENT_VIDEO'] = None #initializing what will be a storage for the current video to be played                        
app.config['PAUSED'] = False                                                                                                      
app.config['LOCAL_VIDEOS'] = dict()                                                                                               
                                                                                                                                  
@app.route('/start') #routeing the following function through 'andy.jokemd.com:5555/start'                                        
def start(): #initializes a ffmpeg process                                                                                        
   subprocess.call(['killall','ffmpeg']) #to prevent any port overlap, killing all other ffmpeg processes                         
   if app.config['MOVIE_PROCESSOR']: #if the 'MOVIE_PROCESSOR' instance refers to something, remove that reference                
        app.config['MOVIE_PROCESSOR'] = None                                                                                      
   current_run = ["./ffmpeg","-re","-i",app.config['CURRENT_VIDEO'],"-af","volume=1.9","-vcodec","libx264","-preset","ultrafast","
-tune","zerolatency","-acodec","aac","-strict","experimental","-ab","512k","-f","flv","rtmp://127.0.0.1:1935/videos/mv"]          
   app.config['MOVIE_PROCESSOR'] = subprocess.Popen(current_run) #sending that command to the command line                        
   return "-SERVER STARTED-" #helpful notification on web page                                                                    
                                                                                                                                  
@app.route('/pause')  #routeing the following function through 'andy.jokemd.com:5555/pause'                                       
def pause(): #pauses teh current ffmpeg process                                                                                   
   if app.config['MOVIE_PROCESSOR']: #if the 'MOVIE_PROCESSOR' instance refers to something                                       
        if not app.config['PAUSED']: #polls for activity                                                                          
                app.config['MOVIE_PROCESSOR'].send_signal(signal.SIGSTOP) #then send a suspend signal to the process              
                app.config['PAUSED'] = True                                                                                       
                return "-SERVER PAUSED-" #helpful notification on webpage                                                         
        app.config['MOVIE_PROCESSOR'].send_signal(signal.SIGCONT) #if 'PAUSED' isnt false or null a resume signal is sent to process                                                                                                                                
        app.config['PAUSED'] = False                                                                                              
        return "-SERVER UNPAUSED-" #helpful notification on webpage                                                               
                                                                                                                                  
   return "-SERVER NOT RUNNING, NOTHING TO BE PAUSED-" #helpful notification on webpage if server isnt running in the first place 
                                                                                                                                  
@app.route('/stop')  #routeing the following function through 'andy.jokemd.com:5555/stop'                                         
def stop(): #completely terminates current fmpeg process                                                                          
                                                                                                                                  
   if not app.config['MOVIE_PROCESSOR'].poll(): #sends a 'poll' to the 'MOVIE_PROCESS' which returns a null value if it is active 
and something else if it isnt                                                                                                     
        while not app.config['MOVIE_PROCESSOR'].poll(): #it will continue to try to terminate the process as long as it poll active                                                                                                                                 
                app.config['MOVIE_PROCESSOR'].kill() #sends a terminate command to the process                                    
                return "-SERVER STOPPED-" #helpful notification on webpage                                                        
                                                                                                                                  
   return "-SERVER NOT RUNNING, NOTHING TO BE STOPPED-" #helpful notification on webpage if server isnt running in the first place
                                                                                                                                  
                                                                                                                                  
@app.route('/videos')   #routeing the following function through 'andy.jokemd.com:5555/stop'                                                                                                            
def show_videos():  #shows all videos                                                                                                           
   vid_list = []   #defines a list                                                                                                            
   path = '.' #the current directory path
     vid_list += [os.path.join(dirpath, f) #the next 3 lines are a statement that fills a list with possible videos with '.mkv' extension
        for dirpath, dirnames, files in os.walk(path)
        for f in fnmatch.filter(files, '*.mkv')]
   vid_list += [os.path.join(dirpath, f)   #the next 3 lines are a statement that fills a list with possible videos with '.mp4' extension
        for dirpath, dirnames, files in os.walk(path)
        for f in fnmatch.filter(files, '*.mp4')]
   vid_list += [os.path.join(dirpath, f)   #the next 3 lines are a statement that fills a list with possible videos with '.avi' extension                                                                                        
        for dirpath, dirnames, files in os.walk(path)                                                                             
        for f in fnmatch.filter(files, '*.avi')]
   keys= [x for x in range(1,len(vid_list))] # makes a list with numbers for all videos
   app.config['LOCAL_VIDEOS'] = dict(zip(keys,vid_list)) #makes a map or 'dict' with keys for each movie for accessing movies
   return str(app.config['LOCAL_VIDEOS'])
 
 
@app.route('/videos/<int:video_number>') #chooses the movie using a variable in the url
def change_video(video_number): #changes the video to the video specified at the numbr_key spot in the dict
   if not app.config['MOVIE_PROCESSOR']: #tests for activity
        if video_number in app.config['LOCAL_VIDEOS'].keys(): #test to make sure key is possible
                app.config['CURRENT_VIDEO'] = app.config['LOCAL_VIDEOS'][video_number] #chooses the video for the global program
                return 'CURRENT VIDEO CHANGED TO \'%s\'' % app.config['LOCAL_VIDEOS'][video_number] #helpful notification on webpage 
        return '\'%s\' NOT IN VIDEO LIBRARY' % app.config['LOCAL_VIDEOS'][video_number] #helpful notification on webpage 
   return 'MOVIE CURRENTLY ACTIVE CANNOT CHANGE!' #helpful notification on webpage if server isnt running in the first place
 
if __name__ =='__main__':  #main method                                                                                     
    app.run(debug=True, host='0.0.0.0', port=5555) #runs the app with specific parameters for server compatibility
