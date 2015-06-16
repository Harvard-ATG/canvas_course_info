
A Harvard-specific Django LTI app that allows course authors to insert a 
"course information" widget containing live-updated course information from the registrar into 
any page with a rich content editor.

It replaces functionality formerly provided by isites.

Authors click an icon, which opens a widget editor window to let them choose
which fields they would like to include in the widget. The widget is then 
inserted into the page, and is live-updated using the icommons api.

In order for the iframes to resize properly, you'll have to add something like the following
to your canvas global js file:

requirejs(["//your.trusted.server/static/js/consumer/iframeResizer.js"], function(iframeResize) {
    iframeResize({log:true});
});

Set log to false once you're satisfied it's working (will emit lots of messages to js console). 

It's annoying that this is neccesary, but that's the way things are with cross-domain iframes.

See https://github.com/davidjbradshaw/iframe-resizer for more details on that.

### See the docs directory for instructions on how to run this app locally and in heroku.
