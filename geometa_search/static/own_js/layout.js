$('a').each(function(){
    console.log($(this).attr('href'));
    $('#link_'+$(this).attr('record_id')).click(function(){
        console.log($(this).attr('title'));
    });
});
