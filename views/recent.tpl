

%for post in passed:
	%post=passed[post]
	<article>
		<header>{{post['title']}}</header>
		
		<section id="dateline">
			Submitted By: {{post['user']}} on {{post['datestamp']}}
		</section>
		
		<section id="body">
			{{post['body']}}
		</section>
	
	</article>
%end


%rebase main globalVars=globalVars
