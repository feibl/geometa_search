$('a').each(function(){
    console.log($(this).attr('href'));
    $('#link_'+$(this).attr('record_id')).click(function(){
        console.log($(this).attr('title'));
    });
});

function displayRecommendations(json_data) {
    recommendations = json_data.results
    console.log(recommendations.length + ' Recommendations');
    var recs = '<h3>Influenced by your History:</h3>' + '<ul>';
    if (recommendations.length > 0) {
        recs += '<ul class="recommendation_list">';
        console.log('Recommendations:');
        for (i = 0; i < recommendations.length; i += 1) {
            console.log(recommendations[i].identifier);
            rec_content = '<li class="recommendation">' +
                '<a href="/show?record_id=' +
                recommendations[i].identifier + '">' +
                recommendations[i].title + '</a></li>';
            
            recs += rec_content;
        }
        recs += '</ul>';
    }
    else {
        recs += '<p>At this point, we do not have any recommendations for you</p>';
    }
    $('#personal_recs').append(recs);
}
function getRecommendations() {
    $.ajax({
        url: '/influenced_by_your_history', 
        async: true,
        dataType: 'json',
        success: displayRecommendations,
        error: function(data) {
            console.log('Error while retrieving recommendations');
        }
    })
}
function refreshRecommender() {
    $.get( "/refresh");
    alert( "Successfully Refreshed." );
}
function displayOtherUsersRecommendations(json_data) {
    recommendations = json_data.results
    console.log(recommendations.length + ' Recommendations');
    if (recommendations.length > 0) {
        var recs = '<h3>Other Users also viewed:</h3>' + '<ul>'
        console.log('Other Users also used Recommendations:');
        for (i = 0; i < recommendations.length; i += 1) {
            console.log(recommendations[i].identifier);
            rec_content = '<li class="recommendation">' +
                '<a href="/show?record_id=' +
                recommendations[i].identifier + '">' +
                recommendations[i].title + '</a></li>';
            
            recs += rec_content;
        }
        recs += '</ul>';
        $('#other_users_viewed').append(recs);
    }
}
function getOtherUsersRecommendations() {
    var record_id = $('#record_data').data("record_id");
    console.log('Other Users also used Recommendations: ' + record_id);
    $.ajax({
        url: '/other_users_also_used', 
        async: true,
        dataType: 'json',
        success: displayOtherUsersRecommendations,
        data: 'record_id=' + record_id,
        error: function(data) {
            console.log('Error while retrieving recommendations');
        }
    })
}
