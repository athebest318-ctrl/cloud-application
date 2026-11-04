import json
from pydantic import ValidationError
from sqlalchemy import inspect
from docs.examples.lecture12_models import Service,ServiceType,ServiceCreate,ServiceRead
payload=ServiceCreate(name='Monitoring Service',status='running',type_id=2)
type_=ServiceType(id=2,name='Monitoring')
item=Service(id=8,**payload.model_dump(),service_type=type_)
assert item in type_.services
assert ServiceRead.model_validate(item).model_dump()=={'id':8,**payload.model_dump()}
assert not inspect(Service).columns.type_id.nullable
assert str(next(iter(inspect(Service).columns.type_id.foreign_keys)).target_fullname)=='service_types.id'
for state in ('running','maintenance','stopped'):ServiceCreate(name='API',status=state,type_id=1)
try:ServiceCreate(name='API',status='unknown',type_id=1)
except ValidationError:rejected=True
else:raise AssertionError('unknown accepted')
print(json.dumps({'orm_table':Service.__tablename__,'columns':list(inspect(Service).columns.keys()),'foreign_key':'services.type_id -> service_types.id','relationship':'ServiceType.services <-> Service.service_type','json':ServiceRead.model_validate(item).model_dump(),'unknown_rejected':rejected,'database_connection':False},ensure_ascii=False,indent=2))
