$("#profile_link").click(function() {
    $("#relationships_section").hide();
    $("#profile_section").show();
    $("#online_section").hide();
    return false;
});

$("#relationships_link").click(function() {
    $("#relationships_section").show();
    $("#profile_section").hide();
    $("#online_section").hide();
    return false;
});

$("#online_link").click(function() {
    $("#relationships_section").hide();
    $("#profile_section").hide();
    $("#online_section").show();
    return false;
});