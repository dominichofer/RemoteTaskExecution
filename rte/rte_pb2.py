# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: rte/rte.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rrte/rte.proto\"\x07\n\x05\x45mpty\"\x15\n\x04\x42ool\x12\r\n\x05value\x18\x01 \x01(\x08\" \n\x04Task\x12\n\n\x02id\x18\x01 \x01(\r\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\"B\n\x0cOptionalTask\x12\x0f\n\x02id\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x11\n\x04\x64\x61ta\x18\x02 \x01(\x0cH\x01\x88\x01\x01\x42\x05\n\x03_idB\x07\n\x05_data\"\x17\n\x06TaskId\x12\r\n\x05value\x18\x01 \x01(\r\"\x16\n\x07TaskIds\x12\x0b\n\x03ids\x18\x01 \x03(\r\".\n\x0eOptionalTaskId\x12\x12\n\x05value\x18\x01 \x01(\rH\x00\x88\x01\x01\x42\x08\n\x06_value\"8\n\x06Result\x12\x0f\n\x07task_id\x18\x01 \x01(\r\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"p\n\x0eOptionalResult\x12\x14\n\x07task_id\x18\x01 \x01(\rH\x00\x88\x01\x01\x12\x14\n\x07success\x18\x02 \x01(\x08H\x01\x88\x01\x01\x12\x11\n\x04\x64\x61ta\x18\x03 \x01(\x0cH\x02\x88\x01\x01\x42\n\n\x08_task_idB\n\n\x08_successB\x07\n\x05_data\"3\n\x0fOptionalResults\x12 \n\x07results\x18\x01 \x03(\x0b\x32\x0f.OptionalResult2\xc2\x02\n\x03Rte\x12&\n\x0bget_next_id\x12\x06.Empty\x1a\x0f.OptionalTaskId\x12\x1c\n\treturn_id\x12\x07.TaskId\x1a\x06.Empty\x12\x19\n\x08\x61\x64\x64_task\x12\x05.Task\x1a\x06.Empty\x12!\n\x08get_task\x12\x06.Empty\x1a\r.OptionalTask\x12\x1d\n\nset_result\x12\x07.Result\x1a\x06.Empty\x12)\n\x0bget_results\x12\x08.TaskIds\x1a\x10.OptionalResults\x12\x1e\n\x0b\x63\x61ncel_task\x12\x07.TaskId\x1a\x06.Empty\x12\"\n\x10is_task_canceled\x12\x07.TaskId\x1a\x05.Bool\x12)\n\x17release_waiting_workers\x12\x06.Empty\x1a\x06.Emptyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'rte.rte_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_EMPTY']._serialized_start=17
  _globals['_EMPTY']._serialized_end=24
  _globals['_BOOL']._serialized_start=26
  _globals['_BOOL']._serialized_end=47
  _globals['_TASK']._serialized_start=49
  _globals['_TASK']._serialized_end=81
  _globals['_OPTIONALTASK']._serialized_start=83
  _globals['_OPTIONALTASK']._serialized_end=149
  _globals['_TASKID']._serialized_start=151
  _globals['_TASKID']._serialized_end=174
  _globals['_TASKIDS']._serialized_start=176
  _globals['_TASKIDS']._serialized_end=198
  _globals['_OPTIONALTASKID']._serialized_start=200
  _globals['_OPTIONALTASKID']._serialized_end=246
  _globals['_RESULT']._serialized_start=248
  _globals['_RESULT']._serialized_end=304
  _globals['_OPTIONALRESULT']._serialized_start=306
  _globals['_OPTIONALRESULT']._serialized_end=418
  _globals['_OPTIONALRESULTS']._serialized_start=420
  _globals['_OPTIONALRESULTS']._serialized_end=471
  _globals['_RTE']._serialized_start=474
  _globals['_RTE']._serialized_end=796
# @@protoc_insertion_point(module_scope)