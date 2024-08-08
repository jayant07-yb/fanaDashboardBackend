    <script type="text/javascript">
        window.onload = function () {
            var data = JSON.parse('[{\u0022timestamp\u0022: \u00222024\u002D08\u002D06T19:44:22.626524+00:00\u0022, \u0022is_active\u0022: 1}, {\u0022timestamp\u0022: \u00222024\u002D08\u002D06T21:19:08.310167+00:00\u0022, \u0022is_active\u0022: 1}, {\u0022timestamp\u0022: \u00222024\u002D08\u002D06T21:19:09.859455+00:00\u0022, \u0022is_active\u0022: 1}]');
            var dataPoints = data.map(function(d) {
                return { x: new Date(d.timestamp), y: d.is_active };
            });

            // Define


            