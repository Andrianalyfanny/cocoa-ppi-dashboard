import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

const CombinedChart = ({ cocoa, ppi }) => {
  const combined = cocoa.map((item, index) => ({
    date: item.date,
    cocoa: item.value,
    ppi: ppi[index]?.value,
  }));

  return (
    <div>
      <h2>Combined Indicators</h2>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={combined}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />

          <Bar dataKey="cocoa" />
          <Line type="monotone" dataKey="ppi" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CombinedChart;