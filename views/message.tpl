
%if (message['error']):
	Error: {{message['error']}}
%elif (message['success']):
	Success: {{message['success']}}
%end

%rebase main globalVars=globalVars