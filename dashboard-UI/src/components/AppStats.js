import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	// eslint-disable-next-line react-hooks/exhaustive-deps
	const getStats = () => {
	
        fetch(`http://acit3855lab.westus.cloudapp.azure.com/stats`)
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
							<th>Referees</th>
							<th>Years of experience</th>
						</tr>
						<tr>
							<td># Referees: {stats['num_of_referees']}</td>
							<td># Number of experience: {stats['num_of_experience']}</td>
						</tr>
						<tr>
							<td colspan="2">Number of fans: {stats['num_of_fans']}</td>
						</tr>
						<tr>
							<td colspan="2">Number of fields: {stats['num_of_fields']}</td>
						</tr>
						<tr>
							<td colspan="2">referee classification: {stats['num_of_class']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
