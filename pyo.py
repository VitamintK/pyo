# -*- coding: utf-8 -*-
from types import ListType
from _pyo import *

######################################################################
### Utilities
######################################################################
def _convertArgsToLists(*args):
    first = True
    for i in args:
        if isinstance(i, PyoObject): pass  
        elif isinstance(i, PyoTableObject): pass 
        elif type(i) != ListType: i = [i]
            
        if first: tup = (i,)
        else: tup = tup + (i,)
        
        first = False
        
    lengths = [len(i) for i in tup]
    max_length = max(lengths)
    tup = tup + (max_length, )  
    return tup

def _wrap(arg, i):
    x = arg[i % len(arg)]
    if isinstance(x, PyoObject):
        return x[0]
    else:
        return x
            
######################################################################
### Proxy of Server object
######################################################################
class Server:
    def __init__(self, sr=44100, nchnls=1, buffersize=64, duplex=0):
        self._server = Server_base(sr, nchnls, buffersize, duplex)
        
    def start(self):
        self._server.start()
    
    def stop(self):
        self._server.stop()
        
    def recstart(self):
        self._server.recstart()
        
    def recstop(self):
        self._server.recstop()
        
    def getStreams(self):
        return self._server.getStreams()
        
    def getSamplingRate(self):
        return self._server.getSamplingRate()
        
    def getNchnls(self):
        return self._server.getNchnls()
        
    def getBufferSize(self):
        return self._server.getBufferSize()

######################################################################
### PyoObject -> base class for pyo sound objects
######################################################################
class PyoObject(object):
    def __init__(self):
        pass

    def __add__(self, x):
        x, lmax = _convertArgsToLists(x)
        return Dummy([obj + _wrap(x,i) for i, obj in enumerate(self._base_objs)])
        
    def __radd__(self, x):
        x, lmax = _convertArgsToLists(x)
        return Dummy([obj + _wrap(x,i) for i, obj in enumerate(self._base_objs)])
            
    def __iadd__(self, x):
        self.setAdd(x)

    def __mul__(self, x):
        x, lmax = _convertArgsToLists(x)
        return Dummy([obj * _wrap(x,i) for i, obj in enumerate(self._base_objs)])
        
    def __rmul__(self, x):
        x, lmax = _convertArgsToLists(x)
        return Dummy([obj * _wrap(x,i) for i, obj in enumerate(self._base_objs)])
            
    def __imul__(self, x):
        self.setMul(x)

    def __getitem__(self, i):
        if i < len(self._base_objs):
            return self._base_objs[i]
        else:
            print "'i' too large!"         
 
    def __len__(self):
        return len(self._base_objs)

    def getBaseObjects(self):
        return self._base_objs
        
    def play(self):
        self._base_objs = [obj.play() for obj in self._base_objs]
        return self

    def out(self, chnl=0):
        self._base_objs = [obj.out(chnl+i) for i, obj in enumerate(self._base_objs)]
        return self
    
    def stop(self):
        [obj.stop() for obj in self._base_objs]

    def mix(self, voices=1):
        return Mix(self, voices)
        
    def setMul(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setMul(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]
        
    def setAdd(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setAdd(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def mul(self):
        pass

    @property
    def add(self):
        pass
        
    @mul.setter
    def mul(self, x):
        self.setMul(x)
        
    @add.setter
    def add(self, x):
        self.setAdd(x)
            
######################################################################
### PyoTableObject -> base class for pyo table objects
######################################################################
class PyoTableObject(object):
    def __init__(self):
        pass

    def __getitem__(self, i):
        if i < len(self._base_objs):
            return self._base_objs[i]
        else:
            print "'i' too large!"         
 
    def __len__(self):
        return len(self._base_objs)

    def getBaseObjects(self):
        return self._base_objs

######################################################################
### Internal classes -> Used by pyo
######################################################################
class Mix(PyoObject):
    def __init__(self, input, voices=1, mul=1, add=0):
        input_objs = input.getBaseObjects()
        if voices < 1: voices = 1
        elif voices > len(input_objs): voices = len(input_objs)
        sub_lists = [[]] * voices
        [sub_lists[i % voices].append(obj) for i, obj in enumerate(input_objs)]
        self._base_objs = [Mix_base(l) for l in sub_lists]
        
class Dummy(PyoObject):
    def __init__(self, objs_list):
        self._base_objs = objs_list

class InputFader(PyoObject):
    def __init__(self, input):
        input, lmax = _convertArgsToLists(input)
        self._base_objs = [InputFader_base(_wrap(input,i)) for i in range(lmax)]

    def setInput(self, x, fadetime=0.05):
        x, lmax = _convertArgsToLists(x)
        [obj.setInput(_wrap(x,i), fadetime) for i, obj in enumerate(self._base_objs)]
         
######################################################################
### Tables
######################################################################                                       
class HarmTable(PyoTableObject):
    def __init__(self, list=[1.], size=8192):
        self._size = size
        self._base_objs = [HarmTable_base(list, size)]
        
    def setSize(self, size):
        [obj.setSize(size) for obj in self._base_objs]
    
    def getSize(self):
        return self._size
        
    def replace(self, list):        
        [obj.replace(list) for obj in self._base_objs]

    @property
    def size(self):
        pass

    @size.setter
    def size(self, x):
        self.setSize(x)
        
class HannTable(PyoTableObject):
    def __init__(self, size=8192):
        self._size = size
        self._base_objs = [HannTable_base(size)]

    def setSize(self, size):
        [obj.setSize(size) for obj in self._base_objs]
    
    def getSize(self):
        return self._size

    @property
    def size(self):
        pass

    @size.setter
    def size(self, x):
        self.setSize(x)

class SndTable(PyoTableObject):
    def __init__(self, path, chnl=None):
        self._snd_size, self._snd_sr, self._snd_chnls = sndinfo(path)
        if chnl == None:
            self._base_objs = [SndTable_base(path, i) for i in range(self._snd_chnls)]
        else:
            self._base_objs = [SndTable_base(path, chnl)]
                
    def getSize(self):
        return self._snd_size
        
    def getRate(self):
        return self._base_objs[0].getRate()

class NewTable(PyoTableObject):
    def __init__(self, length, chnls=1):
        self._base_objs = [NewTable_base(length) for i in range(chnls)]
                
    def getSize(self):
        return self._base_objs[0].getSize()

    def getLength(self):
        return self._base_objs[0].getLength()
             
    def getRate(self):
        return self._base_objs[0].getRate()

class TableRec(PyoObject):
    def __init__(self, input, table, fadetime=0):
        self._in_fader = InputFader(input)
        in_fader, table, fadetime, lmax = _convertArgsToLists(self._in_fader, table, fadetime)
        self._base_objs = [TableRec_base(_wrap(in_fader,i), _wrap(table,i), _wrap(fadetime,i)) for i in range(len(table))]

    def out(self, chnl=0):
        pass

    def setMul(self, x):
        pass
        
    def setAdd(self, x):
        pass    

    def setInput(self, x, fadetime=0.05):
        self._in_fader.setInput(x, fadetime)
      
    @property
    def input(self):
        pass

    @input.setter
    def input(self, x):
        self.setInput(x)
                    
######################################################################
### Sources
######################################################################                                       
class Sine(PyoObject):
    def __init__(self, freq=1000, phase=0, mul=1, add=0):
        freq, phase, mul, add, lmax = _convertArgsToLists(freq, phase, mul, add)
        self._base_objs = [Sine_base(_wrap(freq,i), _wrap(phase,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]
       
    def setFreq(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFreq(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]
        
    def setPhase(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setPhase(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def freq(self):
        pass

    @property
    def phase(self):
        pass

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    @phase.setter
    def phase(self, x):
        self.setPhase(x)
 
class Osc(PyoObject):
    def __init__(self, table, freq=1000, mul=1, add=0):
        table, freq, mul, add, lmax = _convertArgsToLists(table, freq, mul, add)
        self._base_objs = [Osc_base(_wrap(table,i), _wrap(freq,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def setFreq(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFreq(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def freq(self):
        pass

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

class Input(PyoObject):
    def __init__(self, chnl, mul=1, add=0):                
        chnl, mul, add, lmax = _convertArgsToLists(chnl, mul, add)
        self._base_objs = [Input_base(_wrap(chnl,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

class Noise(PyoObject):
    def __init__(self, mul=1, add=0):                
        mul, add, lmax = _convertArgsToLists(mul, add)
        self._base_objs = [Noise_base(_wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

######################################################################
### Controls
######################################################################                                       
class Fader(PyoObject):
    def __init__(self, fadein=0.01, fadeout=0.1, dur=0, mul=1, add=0):
        fadein, fadeout, dur, mul, add, lmax = _convertArgsToLists(fadein, fadeout, dur, mul, add)
        self._base_objs = [Fader_base(_wrap(fadein,i), _wrap(fadeout,i), _wrap(dur,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def out(self, chnl=0):
        pass

    def setFadein(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFadein(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFadeout(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFadeout(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setDur(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setDur(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def fadein(self):
        pass

    @property
    def fadeout(self):
        pass

    @property
    def dur(self):
        pass

    @fadein.setter
    def fadein(self, x):
        self.setFadein(x)

    @fadeout.setter
    def fadeout(self, x):
        self.setFadeout(x)

    @dur.setter
    def dur(self, x):
        self.setDur(x)

######################################################################
### Effects
######################################################################                                       
class Biquad(PyoObject):
    def __init__(self, input, freq=1000, q=1, type=0, mul=1, add=0):
        self._in_fader = InputFader(input)
        in_fader, freq, q, type, mul, add, lmax = _convertArgsToLists(self._in_fader, freq, q, type, mul, add)
        self._base_objs = [Biquad_base(_wrap(in_fader,i), _wrap(freq,i), _wrap(q,i), _wrap(type,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def setInput(self, x, fadetime=0.05):
        self._in_fader.setInput(x, fadetime)
        
    def setFreq(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFreq(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setQ(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setQ(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setType(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setType(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        pass

    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def freq(self):
        pass

    @property
    def q(self):
        pass

    @property
    def type(self):
        pass

    @freq.setter
    def freq(self, x):
        self.setFreq(x)

    @q.setter
    def q(self, x):
        self.setQ(x)

    @type.setter
    def type(self, x):
        self.setType(x)

class Disto(PyoObject):
    def __init__(self, input, drive=.75, slope=.5, mul=1, add=0):
        self._in_fader = InputFader(input)
        in_fader, drive, slope, mul, add, lmax = _convertArgsToLists(self._in_fader, drive, slope, mul, add)
        self._base_objs = [Disto_base(_wrap(in_fader,i), _wrap(drive,i), _wrap(slope,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def setInput(self, x, fadetime=0.05):
        self._in_fader.setInput(x, fadetime)
 
    def setDrive(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setDrive(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setSlope(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setSlope(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        pass

    @input.setter
    def input(self, x):
        self.setInput(x)

    @property
    def drive(self):
        pass

    @property
    def slope(self):
        pass

    @drive.setter
    def drive(self, x):
        self.setDrive(x)

    @slope.setter
    def slope(self, x):
        self.setSlope(x)

class Delay(PyoObject):
    def __init__(self, input, delay=0, feedback=0, maxdelay=44100, mul=1, add=0):
        self._in_fader = InputFader(input)
        in_fader, delay, feedback, maxdelay, mul, add, lmax = _convertArgsToLists(self._in_fader, delay, feedback, maxdelay, mul, add)
        self._base_objs = [Delay_base(_wrap(in_fader,i), _wrap(delay,i), _wrap(feedback,i), _wrap(maxdelay,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def setInput(self, x, fadetime=0.05):
        self._in_fader.setInput(x, fadetime)

    def setDelay(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setDelay(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    def setFeedback(self, x):
        x, lmax = _convertArgsToLists(x)
        [obj.setFeedback(_wrap(x,i)) for i, obj in enumerate(self._base_objs)]

    @property
    def input(self):
        pass

    @input.setter
    def input(self, x):
        self.setInput(x)
 
    @property
    def delay(self):
        pass

    @property
    def feedback(self):
        pass

    @delay.setter
    def delay(self, x):
        self.setDelay(x)

    @feedback.setter
    def feedback(self, x):
        self.setFeedback(x)

######################################################################
### MIDI
######################################################################                                       
class Midictl(PyoObject):
    def __init__(self, ctlnumber, minscale=0, maxscale=1, mul=1, add=0):
        ctlnumber, minscale, maxscale, mul, add, lmax = _convertArgsToLists(ctlnumber, minscale, maxscale, mul, add)
        self._base_objs = [Midictl_base(_wrap(ctlnumber,i), _wrap(minscale,i), _wrap(maxscale,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def out(self, chnl=0):
        pass

######################################################################
### Open Sound Control
######################################################################                                       
class OscSend(PyoObject):
    def __init__(self, input, port, address, host="127.0.0.1"):    
        self._in_fader = InputFader(input)
        in_fader, port, address, host, lmax = _convertArgsToLists(self._in_fader, port, address, host)
        self._base_objs = [OscSend_base(_wrap(in_fader,i), _wrap(port,i), _wrap(address,i), _wrap(host,i)) for i in range(lmax)]
            
    def out(self, chnl=0):
        pass

    def setMul(self, x):
        pass
        
    def setAdd(self, x):
        pass    

    @property
    def input(self):
        pass

    @input.setter
    def input(self, x):
        self.setInput(x)
         
class OscReceive(PyoObject):
    def __init__(self, port, address, mul=1, add=0):    
        address, mul, add, lmax = _convertArgsToLists(address, mul, add)
        self._address = address
        self._mainReceiver = OscReceiver_base(port, address)
        self._base_objs = [OscReceive_base(self._mainReceiver, _wrap(address,i), _wrap(mul,i), _wrap(add,i)) for i in range(lmax)]

    def __getitem__(self, i):
        if type(i) == type(''):
            return self._base_objs[self._address.index(i)]
        elif i < len(self._base_objs):
            return self._base_objs[i]
        else:
            print "'i' too large!"         
             
    def out(self, chnl=0):
        pass
        
        
             