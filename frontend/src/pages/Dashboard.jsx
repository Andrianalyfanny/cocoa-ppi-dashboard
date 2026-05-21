import { useEffect, useState } from "react";
import api from "../api/axios";

import IndicatorsTable from "../components/table/IndicatorsTable";
import CocoaChart from "../components/charts/CocoaChart";
import PPIChart from "../components/charts/PPIChart";
import CombinedChart from "../components/charts/CombinedChart";

const Dashboard = () => {
  const [yearlyData, setYearlyData] = useState(null);
  const [monthlyData, setMonthlyData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      const [yearly, monthly] = await Promise.all([
        api.get("/indicators/yearly"),
        api.get("/indicators/monthly"),
      ]);

      setYearlyData(yearly.data);
      setMonthlyData(monthly.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.center}>
        <h2>Loading dashboard...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.center}>
        <h2 style={{ color: "red" }}>{error}</h2>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Cocoa & PPI Dashboard</h1>

      {/* TABLE SECTION */}
      <div style={styles.card}>
        {yearlyData && <IndicatorsTable data={yearlyData} />}
      </div>

      {/* CHARTS SECTION */}
      <div style={styles.grid}>
        <div style={styles.card}>
          {monthlyData && <CocoaChart data={monthlyData.cocoa} />}
        </div>

        <div style={styles.card}>
          {monthlyData && <PPIChart data={monthlyData.ppi} />}
        </div>

        <div style={styles.cardFull}>
          {monthlyData && (
            <CombinedChart
              cocoa={monthlyData.cocoa}
              ppi={monthlyData.ppi}
            />
          )}
        </div>
      </div>
    </div>
  );
};

/* INLINE STYLES (rapide pour ton test) */
const styles = {
  container: {
    padding: "20px",
    background: "#f4f6f8",
    minHeight: "100vh",
    fontFamily: "Arial",
  },

  title: {
    textAlign: "center",
    marginBottom: "20px",
    color: "#2c3e50",
  },

  grid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "20px",
    marginTop: "20px",
  },

  card: {
    background: "white",
    padding: "15px",
    borderRadius: "10px",
    boxShadow: "0 5px 15px rgba(0,0,0,0.08)",
  },

  cardFull: {
    gridColumn: "1 / -1",
    background: "white",
    padding: "15px",
    borderRadius: "10px",
    boxShadow: "0 5px 15px rgba(0,0,0,0.08)",
  },

  center: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
};

export default Dashboard;