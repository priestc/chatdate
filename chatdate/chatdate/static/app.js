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
    update_relationships();
    return false;
});

$("#online_link").click(function() {
    $("#relationships_section").hide();
    $("#profile_section").hide();
    $("#online_section").show();
    return false;
});

function add_relationship(data) {
    var r = $("#relationship_template").clone();
    r.attr('id', data.id);
    r.find(".name").text(data.name);
    r.addClass('relationship');
    r.find(".status").text(data.status);
    $("#relationships_section").append(r);
}

function update_relationships() {
    $.getJSON(relationships_url, function(relationships) {
        console.log("DDDD", relationships);
        $(".relationship").remove();
        $.each(relationships, function(i, relationship) {
            add_relationship(relationship);
        });
    });
}