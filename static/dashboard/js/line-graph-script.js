// For example on how to intiate graphs, or if you want to mess around with the data / style of these graphs, check the bottom of this panel.
// so the function calls itself first (self-invoking) as a way to keep variables scoped. cause everything else is just main
//and it sets up the classes/tags in the html so that the graph can work
(function ($) {

    $.fn.graphiq = function (options) {

        // Default options
        var settings = $.extend({
            data: {},
            colorLine: "#d3a2ef",
            colorDot: "#c3ecf7",
            colorXGrid: "#7f7f7f",
            colorYGrid: "#7f7f7f",
            colorLabels: "#000000",
            colorUnits: "#000000",
            colorRange: "#000000",
            colorFill: "#533c68",
            colorDotStroke: "#000000",
            dotStrokeWeight: 0,
            fillOpacity: 0.25,
            rangeOpacity: 0.5,
            dotRadius: 3,
            lineWeight: 2,
            yLines: true,
            dots: true,
            xLines: true,
            xLineCount: 5,
            fill: true,
            height: 100,
            fluidParent: null
        }, options);

        var values = [];
        var entryDivision;
        var dataRange = settings.height + settings.dotRadius;
        var parent = this;
        var maxVal;
        var scaleFactor = settings.height / 100;
        var pathPoints = "";
        for (var key in settings.data) {
            values.push(settings.data[key]);
        }

        parent.append(
            '<div class="graphiq__graph-values"></div><div class="graphiq__graph-layout"><svg class="graphiq__graph" viewBox="0 0 960 '+ (settings.height + 10) +'" shape-rendering="geometricPrecision"><path fill="'+ settings.colorFill +'" style="opacity: '+ settings.fillOpacity +'" class="graphiq__fill-path" d="" stroke-width="0" stroke="#000" fill="cyan"/></svg><div class="graphiq__graph-key"></div></div>'
        );
            if (settings.fluidParent) {
                this.closest(".col").css("overflow", "auto");
            }
        parent.addClass('graphiq');

        var graph = this.find(".graphiq__graph");

        // Get data from table
        for (var key in settings.data) {
            this.find(".graphiq__graph-key").append('<div class="key" style="color: ' + settings.colorLabels + '">' + key + "</div>");
        }

        maxVal = Math.max.apply(Math, values);


        this.find('.graphiq__graph-values').append('<span style="color: ' + settings.colorRange + '; opacity: ' + settings.rangeOpacity + '">' + maxVal + '</span><span style="color: ' + settings.colorRange + '; opacity: ' + settings.rangeOpacity + '" >0</span>');



        // Set even spacing in the graph depending on amount of data

        var width = parent.find(".graphiq__graph-layout").width();

        if (settings.xLines) {
            unitLines(width, maxVal);
        }

        layoutGraph(width, true);

        $(window).on("resize", function () {
            pathPoints = "";
            width = parent.find(".graphiq__graph-layout").width();
            layoutGraph(width, false);
        });

       // buildFillPath();

        function percentageOf(max, current) {
            return (current / max * 100) * scaleFactor;
        }

        function layoutGraph(width, initial) {
            graph.attr({
                viewBox: "0 0 " + width + " " + (settings.height + 10),
                width: width
            });
            entryDivision = width / (values.length - 1);
            getCoordinates(initial, entryDivision);
        }

        function getCoordinates(initial, entryDivision) {


            for (i = 0; i < values.length; i++) {

                var offset;

                if (i == 0) {
                    offset = (settings.dotRadius + (settings.dotStrokeWeight)) + 1;
                }

                 else if (i == values.length - 1) {
                    offset = ((settings.dotRadius + (settings.dotStrokeWeight )) * -1) - 1;
                } else {
                    offset = 0;
                }

                var lineOffset = i == values.length - 2 ? (settings.dotRadius + (settings.dotStrokeWeight)) / 2 : 0;

                let nextI = i + 1;
                let xAxis = (entryDivision * i) + offset;
                let xAxis2 = entryDivision * nextI;

                console.log(offset);


                let yAxis = dataRange - percentageOf(maxVal, values[i]);

                let yAxis2 = dataRange - percentageOf(maxVal, values[nextI]);

                if (i == values.length - 1) {
                    yAxis2 = yAxis;
                    xAxis2 = xAxis;
                }

              pathPoints += " L " + xAxis + " " + yAxis;


                if (i == values.length - 1 && settings.fill) {
                    buildFillPath(pathPoints);
                }

                if (initial) {

                    if (settings.yLines) {

                    $(document.createElementNS("http://www.w3.org/2000/svg", "line"))
                        .attr({
                            class: "graphiq__y-division",
                            x1: xAxis,
                            y1: yAxis,
                            x2: xAxis,
                            y2: settings.height + 5,
                            stroke: settings.colorYGrid,
                            "stroke-dasharray": "5 6",
                            "stroke-width": 1
                        })
                        .prependTo(graph);

                    }

                    // Draw the line


                    $(document.createElementNS("http://www.w3.org/2000/svg", "line"))
                        .attr({
                            class: "graphiq__line",
                            x1: xAxis ,
                            y1: yAxis,
                            x2: xAxis2 - lineOffset,
                            y2: yAxis2 + (settings.dotStrokeWeight / 2),
                            stroke: settings.colorLine,
                            "stroke-width": settings.lineWeight,
                            "vector-effect": "non-scaling-stroke"
                        }).appendTo(graph);

                    // Draw the circle


                    $(document.createElementNS("http://www.w3.org/2000/svg", "circle"))
                        .attr({
                            class: "graphiq__graph-dot",
                            cx: xAxis,
                            cy: yAxis + (settings.dotStrokeWeight / 2),
                            r: settings.dots ? settings.dotRadius : 0,
                            fill: settings.colorDot,
                            stroke: settings.colorDotStroke,
                            "stroke-width": settings.dotStrokeWeight,
                            "data-value": values[i],
                            "vector-effect": "non-scaling-stroke"
                        })
                        .appendTo(graph);


                    // Resize instead of draw, used in resize
                } else {

                    parent.find(".graphiq__graph-dot")
                        .eq(i)
                        .attr({
                            cx: xAxis,
                        });
                    parent.find(".graphiq__line")
                        .eq(i)
                        .attr({
                            x1: xAxis,
                            x2: xAxis2 - lineOffset,
                        });
                    parent.find(".graphiq__y-division")
                        .eq(values.length - i - 1)
                        .attr({
                            x1: xAxis,
                            x2: xAxis
                        });
                    parent.find(".graphiq__x-line").each(function () {
                        $(this).attr({
                            x2: width
                        });
                    });
                }
            }
        }

        function buildFillPath(pathPoints) {

          parent.find('.graphiq__fill-path').attr("d", "M  " + (4 + settings.dotStrokeWeight) + " " + (settings.height + 5 + settings.dotStrokeWeight) + pathPoints +  " L " + (width - settings.dotRadius - settings.dotStrokeWeight) + " " + (settings.height + 5 + settings.dotStrokeWeight))
        }

        function unitLines(width, maxVal) {
            // Draw the max line

            var iteration = 100 / (settings.xLineCount - 1);


                for (i=0; i < settings.xLineCount; i++) {

                        $(document.createElementNS("http://www.w3.org/2000/svg", "line"))
                        .attr({
                            class: "graphiq__x-line",
                            y1: iteration * i + (settings.dotRadius + settings.dotStrokeWeight),
                            x2: width,
                            y2: iteration * i +  (settings.dotRadius + settings.dotStrokeWeight),
                            stroke: settings.colorXGrid,
                            // "stroke-dasharray": "5 6",
                            "stroke-width": 1
                        })
                        .prependTo(graph);

                }

        }

        parent.hover(function () {

            $(this).find('.graphiq__graph-dot').each(function (index) {
                $('body').append('<span style="color: '+ settings.colorUnits +'" class="graphiq__value-dialog value-'
                + index + '">' + $(this).attr("data-value") + '</span>');
                $('.value-' + index).css({
                    top: $(this).position().top - 20,
                    left: $(this).position().left - ($('.value-' + index).outerWidth() / 2) + 3
                })
            })
        }, function () {
            $('.graphiq__value-dialog').remove();
        })

    };

}(jQuery));

// Initiate graphs
const dataSales = document.querySelector("#graph-sales");

const sales = JSON.parse(document.getElementById('sales-data').textContent);

$('.graph-sales').graphiq({
    data: sales,
    fluidParent: ".col",
    height: 100,
    xLineCount: 5,
    dotRadius: 4,
    yLines: true,
    xLines: true,
    dots: true,
    fillOpacity: 0.5,
    fill: true,
    colorUnits: "#1010C3"
  });