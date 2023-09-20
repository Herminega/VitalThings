from pydantic import BaseModel, parse_obj_as, parse_raw_as, root_validator
from datetime import datetime
from typing import Optional, Literal, Union, Dict, List, Any
import json
from devtools import debug

class SomnofyDeviceLogBaseRecordPayload(BaseModel):

    @property
    def warning(self) -> bool:
        return False

    class Config:
        extra = "allow"


class SomnofyDeviceLogBaseRecord(BaseModel):
    timestamp_device: datetime
    timestamp_server: datetime 

    context: Optional[str]
    type: str

    payload: SomnofyDeviceLogBaseRecordPayload

    @property
    def warning(self) -> bool:
        return self.payload.warning

    class Config:
        fields = {
            'id': '_id',
            'timestamp_device': 'Timestamp',
            'timestamp_server': 'TimestampServer',
            'type': 'Type',
            'context': 'Context',
            'payload': 'Payload'
            }
        json_encoders = {
        }


class SomnofyDeviceLogBootRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    system_version: Optional[str]
    xethru_module: Optional[str]
    xethru_version: Optional[str]
    comm_version: Optional[str]
    reset_reason: Optional[str]
    reset_count: Optional[int]
    base_mac: Optional[str]
    fatal_info: Optional[List[int]]

    @property
    def warning(self) -> bool:
        
        if self.fatal_info:
            return True
        
        if self.reset_count and self.reset_count > 5:
            return True
        
        return False

    class Config:
        extra = "allow"
        fields = {
            'system_version': 'SystemVersion',
            'xethru_module': 'XeThruModule',
            'xethru_version': 'XeThruVersion',
            'comm_version': 'CommVersion',
            'reset_reason': 'ResetReason',
            'reset_count': 'ResetCount',
            'base_mac': 'BaseMac',
            'startup_light': 'StartupLight',
            'fatal_info': 'FatalInfo',
        }   


class SomnofyDeviceLogBootRecord(SomnofyDeviceLogBaseRecord):
    type: Literal['Boot']

    payload: SomnofyDeviceLogBootRecordPayload


class SomnofyDeviceLogXeThruStartupRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    count: Optional[int]
    success: Optional[bool]
    state: Optional[str]

    class Config:
        extra = "allow"
        fields = {
            'count': 'Count',
            'success': 'Success',
            'state': 'State',
        }   


class SomnofyDeviceLogXeThruStartupRecord(SomnofyDeviceLogBaseRecord):
    type: Literal['XeThruStartup']
    payload: SomnofyDeviceLogXeThruStartupRecordPayload


class SomnofyDeviceLogPingRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    voltage: Optional[float]

    class Config:
        extra = "allow"
        fields = {
            'voltage': 'Voltage',
        }        


class SomnofyDeviceLogPingRecord(SomnofyDeviceLogBaseRecord):
    type: Literal['Ping']
    payload: SomnofyDeviceLogPingRecordPayload


class SomnofyDeviceLogCommResetRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    count: Optional[int]

    @property
    def warning(self) -> bool:
        
        if self.count and self.count > 5:
            return True
        
        return False

    class Config:
        extra = "allow"
        fields = {
            'count': 'Count',
        }       

class SomnofyDeviceLogCommResetRecord(SomnofyDeviceLogBaseRecord):
    # context: Literal['System']
    type: Literal['CommReset']
    payload: SomnofyDeviceLogCommResetRecordPayload


class SomnofyDeviceLogAlarmRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    session_id: Optional[str]
    state: Optional[str]
    event: Optional[str]

    class Config:
        extra = "allow"
        fields = {
            'session_id': 'SessionID',
            'state': 'State',
            'event': 'Event',
        }    


class SomnofyDeviceLogAlarmRecord(SomnofyDeviceLogBaseRecord):
    type: Literal['Alarm']
    payload: SomnofyDeviceLogAlarmRecordPayload


class SomnofyDeviceLogGuidedBreathingRecordPayload(SomnofyDeviceLogBaseRecordPayload):
    session_id: Optional[str]
    state: Optional[str]
    guide_rpm: Optional[int]

    class Config:
        extra = "allow"
        fields = {
            'session_id': 'SessionID',
            'state': 'State',
            'guide_rpm': 'GuideRpm'
        }    


class SomnofyDeviceLogGuidedBreathingRecord(SomnofyDeviceLogBaseRecord):
    type: Literal['GuidedBreathing']
    payload: SomnofyDeviceLogGuidedBreathingRecordPayload



AnySomnofyDeviceLogRecord = Union[
    SomnofyDeviceLogBootRecord, 
    SomnofyDeviceLogPingRecord, 
    SomnofyDeviceLogCommResetRecord, 
    SomnofyDeviceLogAlarmRecord,
    SomnofyDeviceLogGuidedBreathingRecord,
    SomnofyDeviceLogXeThruStartupRecord,
    SomnofyDeviceLogBaseRecord
]

def pre_process(data: str):

    record = json.loads(data)

    #Get old format on new format
    if 'ContentType' in record:
        if 'XeThruStartup' in record['Content']:
            record['Type'] = 'XeThruStartup'
            record['Content'] = record['Content']['XeThruStartup']
        elif 'CommReset' in record['Content']:
            record['Type'] = 'CommReset'
            record['Content']['Count'] = record['Content'].pop('CommReset')
        else:
            record['Type'] = record.pop('ContentType')

        if 'Status' in record['Content']:
            status = record['Content'].pop('Status')
            record['Content'] = { **record['Content'], **status } 

        record['Payload'] = record.pop('Content')

    try:
        timestamp = datetime.fromisoformat(record['Timestamp']).isoformat()
    except ValueError:
        # Assume old time format
        timestamp = datetime.strptime(record['Timestamp'], '%Y%m%d-%H%M%S').isoformat()
    record['Timestamp'] = timestamp

    try:
        timestamp_server = datetime.fromtimestamp(record['TimestampServer']/1000).isoformat()
        record['TimestampServer'] = timestamp_server
    except Exception as e:
        pass
    return record


output = open("devicelog_processed.json", "w")

c = 0
with open("devicelogs.json", "rb") as fp:
    #reading json file line by line, saves memory
    while l := fp.readline():
        try:
            #get data on standard form, not pydantic
            record = pre_process(l)
            output.write(json.dumps(record) + "\n")      

            #data process with pydantic, did not work. There's a situation with the timestamp that we're not handling.  
            #record = parse_obj_as(AnySomnofyDeviceLogRecord, pre_process(l))
            #output.write(record.json() + "\n")      
        except Exception:
            print(f'unable to parse line {c}')
        
        if c % 10000 == 0:
            print(c)

        c += 1

output.close()

print("Done")
