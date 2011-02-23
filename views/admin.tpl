<h2>Admin Page</h2>
<section id="admin">
	<fieldset id="userInfo">
		<ul>
			<li>Username: {{userInfo['userName']}}</li>
			<li>Real Name: {{userInfo['realName']}}</li>
			<li>Email: {{userInfo['email']}}</li>
		</ul>
	</fieldset>
	
	
	<fieldset id="permissions">
		<h4>Permissions: </h4>
		
	</fieldset>
</section>

%rebase main globalVars=globalVars