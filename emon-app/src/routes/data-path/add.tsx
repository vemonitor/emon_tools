import { AddActionType } from "@/lib/types";
import { DataPathForm, DataPathFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";

const AddDataPathAction = async(
  values: DataPathFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): AddActionType => {
  
  const data = {
      ...values,
      id: undefined
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/data_path/add/`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }
    ).then((response) => response.json())
    if (!response.success) {
      return {
        success: false,
        msg: response.msg,
        errors: response.errors,
        from_error: response.from_error,
      }
    }
  } catch (error: unknown) {
    console.log('Error fetching data:', error);
    return {
      success: false,
      msg: 'Unable to save data, please control all fields',
      error: error instanceof Error ? error.message : 'Unknown error'
    }
  }

  return {success: true, redirect: `/data-path`};
};

function AddDataPath() {
  const { fetchWithAuth } = useAuth();
  return (
    <div>
      <DataPathForm
        handleSubmit={(values: DataPathFormType) => AddDataPathAction(values, fetchWithAuth)}
      />
    </div>
  )
}

export default AddDataPath

