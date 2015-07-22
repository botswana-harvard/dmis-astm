# dmis-astm

Export result data from the DMIS LIS as ASTM.

Uses `python-astm`.

Use the `start_client` management command to start the ASTM client: 
	
	>>> python manage.py start_client localhost 15200
	
	Connecting to 127.0.0.1 on port 15200 ...
	Press CTRL-C to interrupt.
	
	Sending: 100% 1114/1114 (id=1854134)
	
	Closed 

The client is the `astm.Client`. It takes a custom emitter. The default client in `dmis-astm` uses `result_emitter`
from `dmis-astm.result_emitter`.

See also `getresults` and `getresults-astm`.

The `History` model keeps track of what has been sent. See `dmis-astm.dmis_history`.
