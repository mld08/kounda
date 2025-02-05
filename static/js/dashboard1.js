$(function () {
    // Récupération des données dynamiques depuis Flask
    $.getJSON("/api/dashboard-data", function(data) {
  
      // =====================================
      // Profit (Bar Chart)
      // =====================================
      var chart = new ApexCharts(document.querySelector("#chart"), {
        series: [
          { name: "Gains du mois", data: data.earnings },
          { name: "Depenses du mois", data: data.expenses },
        ],
        chart: {
          type: "bar",
          height: 345,
          offsetX: -15,
          toolbar: { show: true },
        },
        colors: ["#5D87FF", "#49BEFF"],
        xaxis: {
          categories: data.dates
        },
      });
  
      chart.render();
  
      // =====================================
      // Breakup (Pie Chart des projets)
      // =====================================
      var breakup = new ApexCharts(document.querySelector("#breakup"), {
        series: [data.projets["en attente"] || 0, data.projets["en cours"] || 0, data.projets["terminé"] || 0, data.projets["annulé"] || 0],
        labels: ["En attente", "En cours", "Terminé", "annulé"],
        chart: {
          type: "donut",
          width: 270,
        },
        colors: ["#FFC107", "#0DCAF0", "#198754", "#DC3545"],
      });
  
      breakup.render();
  
      // =====================================
      // Earnings (Line Chart)
      // =====================================
      var earning = {
        chart: {
          id: "sparkline3",
          type: "area",
          height: 60,
          sparkline: {
            enabled: true,
          },
          group: "sparklines",
          fontFamily: "Plus Jakarta Sans', sans-serif",
          foreColor: "#adb0bb",
        },
        series: [
          {
            name: "Earnings",
            color: "#49BEFF",
            data: data.earnings, // Utiliser les données de l'API Flask
          },
        ],
        stroke: {
          curve: "smooth",
          width: 2,
        },
        fill: {
          colors: ["#f3feff"],
          type: "solid",
          opacity: 0.05,
        },
        markers: {
          size: 0,
        },
        tooltip: {
          theme: "dark",
          fixed: {
            enabled: true,
            position: "right",
          },
          x: {
            show: false,
          },
        },
      };
  
      new ApexCharts(document.querySelector("#earning"), earning).render();
    });
  });
  