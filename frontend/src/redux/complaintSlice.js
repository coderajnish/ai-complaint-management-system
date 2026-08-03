import { createSlice } from "@reduxjs/toolkit";

const complaintSlice = createSlice({
  name: "complaint",
  initialState: {},
  reducers: {
    setComplaint: (state, action) => {
      return action.payload;
    },
    clearComplaint: () => {
      return {};
    }
  },
});

export const { setComplaint, clearComplaint } = complaintSlice.actions;
export default complaintSlice.reducer;