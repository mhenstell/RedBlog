<section id="header">
	<section id="siteTitle">
		<a href="/">{{globalVars['siteTitle']}}</a>
	</section id="siteTitle">
	<section id="info">
		Info
	</section>
	%if (globalVars['loggedInUser']):
		<section id="user">
			{{globalVars['loggedInUser']}}
		</section>
	%else:
		Not logged in
	%end
</section>