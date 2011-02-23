<section id="postForm">
	<form action="/post" method="post" enctype="multipart/form-data">
	  <fieldset>
	  	<label for="title">Title: </label>
	  	<input id="title" name="title" type="text" />
	  </fieldset>
	  <fieldset>
	  	<label for="body">Body: </label>
	  	<textarea id="body" name="body"></textarea>
	  </fieldset>
	  <fieldset class="submit">
	  	<input type="submit" value="Submit" />
	  </fieldset>
</form>
</section>

%rebase main globalVars=globalVars