var base = {

    // use for reload div
    reloadData : function(division){
        $.get(location.href, function(data) {
            $(`${division}`).html($(data).find(`${division}`).html());
        });
    },

    // use for replace div with new one
    replaceDiv : function(division, htmlData){
        $(`${division}`).html($(htmlData).find(`${division}`).html());

    },
    
    //Reload div from url
    ReloadDiv : function(division){
        $(`${division}`).load(window.location.href + ` ${division} > *`);
        // $("#verify_request_count").load(window.location.href + " #verify_request_count > *");
    }

}