import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://easyeats.eastus.cloudapp.azure.com/processing/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Order</th>
							<th>Delivery</th>
						</tr>
						<tr>
							<td># Orders: {stats['num_orders']}</td>
							<td># Deliveries: {stats['num_deliveries']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Price Purchase: {stats['max_price_purchase']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Delivery Distance: {stats['max_distance_delivery']}</td>
						</tr>
						<tr>
							<td colspan="2">Avg Price Purchase: {stats['avg_price_purchase']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
