

%for post in posts:

	<article>
		<header>{{posts[post]['title']}}</header>
		
		<section id="dateline">
			Submitted By: {{posts[post]['user']}} on {{posts[post]['datestamp']}}
		</section>
		
		<section id="body">
			{{posts[post]['body']}}
		</section>
	
	</article>
%end


%rebase main globalVars=globalVars