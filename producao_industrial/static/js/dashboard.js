<script>
const ligadas = Number("{{ ligadas }}");
const manutencao = Number("{{ manutencao }}");
const paradas = Number("{{ paradas }}");

const ctx = document.getElementById('grafico').getContext('2d');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Ligadas', 'Manutenção', 'Paradas'],
        datasets: [{
            label: 'Status das Máquinas',
            data: [ligadas, manutencao, paradas],
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                labels: {
                    color: 'white'
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: 'white'
                }
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: 'white'
                }
            }
        }
    }
});
</script>