import React, {useState} from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import {Bar} from 'react-chartjs-2';
import {Box, TextField} from "@material-ui/core";

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export const options = {
    responsive: true,
    plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: 'Chart.js Bar Chart',
        },
    },
};

export function App() {
    const [labels, setLabels] = useState(['Skills'])
    const [datasets, setDatasets] = useState([])

    const search = (e) => {
        fetch(`http://192.168.1.7:8000/api/v1/get-stats/${e.target.value}`)
            .then(response => response.json())
            .then(responseJson => {
                let sets = [];
                for (const x of responseJson) {
                    sets.push({
                        "label": x.name,
                        "data": [x.count],
                        "backgroundColor": `#${Math.floor(Math.random()*16777215).toString(16)}`,
                    })
                }
                setDatasets(sets);
            })
    }

    return (
        <>
            <Box
                style={{textAlign: "center"}}
                children={
                    <TextField
                        style={{width: "70%", marginTop: 20, marginBottom: 30}}
                        onKeyPress={(ev) => {
                            if (ev.key === 'Enter') {
                                search(ev)
                            }
                        }}
                        label="Position"
                    />
                }
            />
            <Bar options={options} data={{labels, datasets}}/>
        </>
    )
}