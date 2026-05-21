const getColor = (value) => {
  if (value > 0) return "green";
  if (value < 0) return "red";
  return "black";
};

const IndicatorsTable = ({ data }) => {
  return (
    <table border="1" cellPadding="10" style={{ width: "100%", textAlign: "center" }}>
      <thead>
        <tr>
          <th>Indicators</th>
          <th>2020</th>
          <th>2021</th>
          <th>2022</th>
          <th>2023</th>
          <th>2024</th>
          <th>2025</th>
          <th>2026</th>
        </tr>
      </thead>

      <tbody>

        {/* ================= COCOA ================= */}

        <tr>
          <td><b>Cocoa Price</b></td>
          {data.cocoa.map((item) => (
            <td key={`cp-${item.year}`}>
              {item.avg_value?.toFixed(2)}
            </td>
          ))}
        </tr>

        <tr>
          <td>Cocoa Price Change</td>
          {data.cocoa.map((item) => (
            <td
              key={`cpc-${item.year}`}
              style={{ color: getColor(item.yoy_change) }}
            >
              {item.yoy_change?.toFixed(2)}
            </td>
          ))}
        </tr>

        <tr>
          <td>Cocoa Price % Change</td>
          {data.cocoa.map((item) => (
            <td
              key={`cpp-${item.year}`}
              style={{ color: getColor(item.yoy_pct_change) }}
            >
              {item.yoy_pct_change?.toFixed(2)}%
            </td>
          ))}
        </tr>

        {/* ================= PPI ================= */}

        <tr>
          <td><b>PPI</b></td>
          {data.ppi.map((item) => (
            <td key={`ppi-${item.year}`}>
              {item.avg_value?.toFixed(2)}
            </td>
          ))}
        </tr>

        <tr>
          <td>PPI Change</td>
          {data.ppi.map((item) => (
            <td
              key={`ppic-${item.year}`}
              style={{ color: getColor(item.yoy_change) }}
            >
              {item.yoy_change?.toFixed(2)}
            </td>
          ))}
        </tr>

        <tr>
          <td>PPI % Change</td>
          {data.ppi.map((item) => (
            <td
              key={`ppip-${item.year}`}
              style={{ color: getColor(item.yoy_pct_change) }}
            >
              {item.yoy_pct_change?.toFixed(2)}%
            </td>
          ))}
        </tr>

        <tr>
          <td>PPI % Change Reference</td>
          {data.ppi.map((item) => (
            <td
              key={`ppir-${item.year}`}
              style={{ color: getColor(item.pct_change_ref) }}
            >
              {item.pct_change_ref?.toFixed(2)}%
            </td>
          ))}
        </tr>

      </tbody>
    </table>
  );
};

export default IndicatorsTable;