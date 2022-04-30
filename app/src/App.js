import React, {useEffect, useState} from 'react';
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
import {Autocomplete} from '@material-ui/lab'

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

export function App() {
    const [labels, setLabels] = useState(['Skills'])
    const [datasets, setDatasets] = useState([])
    const [positions, setPositions] = useState([])
    const [position, setPosition] = useState("")

    const options = {
        responsive: true,
        barPercentage: 5,
        plugins: {
            legend: {
                position: "top"
            },
            title: {
                display: true,
                text: position,
                font: {
                    size: 22
                }
            },
        },
    };

    useEffect(() => {
        fetch("http://192.168.1.7:8000/api/v1/positions")
            .then(response => response.json())
            .then(responseJson => {
                setPositions(responseJson);
            })
    }, [])

    const search = (e) => {
        fetch(`http://192.168.1.7:8000/api/v1/get-stats/${e.target.value}`)
            .then(response => response.json())
            .then(responseJson => {
                let sets = [];
                for (const x of responseJson) {
                    sets.push({
                        "label": x.name,
                        "data": [x.count],
                        "backgroundColor": `#${Math.floor(Math.random() * 16777215).toString(16)}`,
                    })
                }
                setDatasets(sets);
            })
    }

    return (
        <Box className="chartWrapper">
            <Box
                style={{textAlign: "center"}}
                children={
                    <Autocomplete
                        style={{width: "70%", marginLeft: "auto", marginRight: "auto", marginTop: 20, marginBottom: 30}}
                        options={positions}
                        getOptionLabel={(option) => option.name}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter') {
                                setPosition(e.target.value);
                                search(e);
                            }
                        }}
                        sx={{width: 300}}
                        renderInput={(params) =>
                            <TextField
                                {...params}
                                label="Movie"
                            />
                        }
                    />
                    //     <TextField
                    //     style={{width: "70%", marginTop: 20, marginBottom: 30}}
                    //     onKeyPress={(ev) => {
                    //     if (ev.key === 'Enter') {
                    //     search(ev)
                    // }
                    // }}
                    //     label="Position"
                    //     />
                }
            />
            <Box>
                <Bar options={options} data={{labels, datasets}} type={null}/>
            </Box>
        </Box>
    )
}