import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthChecks() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [statuses, setStatuses] = useState({});
    const [error, setError] = useState(null);
    const currentDate = new Date();

	const getHealthChecks = () => {
	
        fetch(`http://easyeats.eastus.cloudapp.azure.com/health_check/health_checks`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Health Checks")
                setStatuses(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getHealthChecks(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getHealthChecks]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        const statusDate = new Date(statuses['last_updated']);
        const dateDiff = (currentDate.getTime() - statusDate.getTime()) / 1000;
        return(
            <div>
                <h1>Service Health Statuses</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Services</th>
							<th>Health Status</th>
						</tr>
						<tr>
							<td>Receiver:</td>
							<td>{statuses['receiver']}</td>
						</tr>
						<tr>
							<td>Storage:</td>
							<td>{statuses['storage']}</td>
						</tr>
                        <tr>
							<td>Processing:</td>
							<td>{statuses['processing']}</td>
						</tr>
                        <tr>
							<td>Audit:</td>
							<td>{statuses['audit']}</td>
						</tr>
                        <tr>
							<td>Last Updated:</td>
							<td>{round(dateDiff)} seconds ago</td>
						</tr>
					</tbody>
                </table>
            </div>
        )
    }
}
