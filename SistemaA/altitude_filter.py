import datetime
import struct
from filter_framework import FilterFramework


class AltitudeFilter(FilterFramework):
    """ This class serves as an example for using the SinkFilterTemplate for creating a sink filter. This particular
        filter reads some input from the filter's input port and does the following:

        1) It parses the input stream and "decommutates" the measurement ID
        2) It parses the input steam for measurments and "decommutates" measurements, storing the bits in a long word.

        This filter illustrates how to convert the byte stream data from the upstream filterinto useable data found in
        the stream: namely time (long type) and measurements (double type).
        """
        
    def __init__(self):
        FilterFramework.__init__(self)
        
        
    def run(self):
        """ TimeStamp is used to compute time .
		    TimeStampFormat is used to format the time value so that it can be easily printed
		    to the terminal.
            """
                   
        measurementLength = 8  # This is the length of all measurements (including time) in bytes
        idLength = 4
                    # This is the length of IDs in the byte stream
        
        dataByte = 0            # This is the data byte read from the stream
        bytesRead = 0           # This is the number of bytes read from the stream
        bytesdiscarted=0		# This is the number of bytes descarted from the
        byteswritten=0
        measurement = 0         # This is the word used to store all measurements - conversions are illustrated.
        idMeasurement = 0       # This is the measurement id
        
        # We announce to the world that we are alive ...
        print "{0}::AltitudeFilter reading".format(self.getName())
        
        while True:
            try:
                """ We know that the first data coming to this filter is going to be an ID and
				    that it is IdLength long. So we first decommutate the ID bytes.
                    """
                                               
                idMeasurement = 0
                i = 0
      
                while i < idLength:
                    dataByte = self.readFilterInputPort() # This is where we read the byte from the stream...                      
                    self.writeFilterOutputPort(dataByte)
                    idMeasurement = idMeasurement << 8     # We append the byte on to ID ...
                    idMeasurement = idMeasurement | dataByte                
                    bytesRead += 1
                    i += 1
                
                                             
                measurement = 0                
                i = 0
                while i < measurementLength:
                    dataByte = self.readFilterInputPort()
                    if(idMeasurement==2):
                        measurement = measurement << 8
                        measurement = measurement | dataByte
                    else:
                        self.writeFilterOutputPort(dataByte)
                        byteswritten+=1                    
                    bytesRead += 1
                    i += 1                                                    
                    
                if idMeasurement == 2:
                    #convertimos la medida de 8 bytes en un arreglo de 8 bytes
                    byteArray = struct.pack("@Q", measurement) 
                
                    #convertimos el arreglo de 8 bytes en un numero decimal
                    doubleValue = struct.unpack('d', byteArray)[0]                        
                                        
                    c=doubleValue*0.3048                                                                                       
                    d=struct.pack('d', c) 
                    v=struct.unpack("@Q", d)[0] 
                    print "ID = {0} Altitud {1} Metros {2} medida {3} unpack {4} ".format(idMeasurement, doubleValue, c, measurement, v)                                                       
                    dataByteTmp=0
                    j=7 
                    while j >= 0:
                        m= v >> 8 * j     # We append the byte on to ID ...                        
                        dataByteTmp = m & 255                        
                        self.writeFilterOutputPort(dataByteTmp)                                                
                        byteswritten+=1
                        j-=1                       
                                              
            except:
                self.closePorts()
                print "{0}::AltitudeFilter; bytes read: {1}, bytes written:{2}".format(self.getName(), bytesRead, byteswritten)
                break