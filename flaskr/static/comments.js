//turn text into a textarea form    
function commentSetup(){
    $(".editcomment").click(function(event){
        var id = $(this).data("id");

        var divHtml = $("#comment"+id).text();
        var editableText = $("<textarea id='comment"+id+"' class='commentTextArea' />");
        editableText.val(divHtml);
        $("#comment"+id).replaceWith(editableText);
        editableText.focus();
        $("#commentEdit"+id).hide();
        $("#commentSubmit"+id).show();
    })
    $(".submitComment").on("click",submitCommentUpdate);
    $(".deleteComment").on("click",deleteComment);
    $(".createComment").on("click",createComment);
}

//submit update function
//with ajax to blog.updateComment
function submitCommentUpdate(){
    var id = $(this).data("id");
    var textOBJ = $("#comment"+id);
    var text = textOBJ.val();
    $.ajax({
            method: "POST",
            url: $SCRIPT_ROOT+"/ajax/comment/"+id+"/update",
            data: {body: text}
        })
        .done(function() {
        })
        .fail(function() {
            alert( "error" );
        });
    $("#commentEdit"+id).show();
    $("#commentSubmit"+id).hide();
    var viewableText = $("<div id='comment"+id+"' class='commentDiv' />");
    viewableText.text(text);
    $(textOBJ).replaceWith(viewableText);
}


//delete confirmation dialog, ajax to blog.deleteComment
function deleteComment(){
    var id = $(this).data("id");
    var textOBJ = $("#comment"+id);
    $.ajax({
            method: "POST",
            url: $SCRIPT_ROOT+"/ajax/comment/"+id+"/delete"
        })
        .done(function() {  
            textOBJ.parents(".comment").remove();
        })
        .fail(function() {
            alert( "error" );
        });
}


//create comment function
//with ajax to blog.createComment
function createComment(){
    var postid = $(this).data("postid");
    var text = $("#newCommentText").val();
    $.ajax({
            method: "POST",
            url: $SCRIPT_ROOT+"/ajax/comment/"+postid+"/create",
            data: {body: text}
        })
        .done(function() {
            location.reload();
        })
        .fail(function() {
            alert( "error" );
        });
}
