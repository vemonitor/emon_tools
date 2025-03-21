import { AddActionType, EditCrudComponentProps, EmonHostEdit } from "@/lib/types";
import { EmonHostForm, EmonHostFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";

const AddEmonHostAction = async(
  values: EmonHostFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): AddActionType => {

  const data = {
      ...values,
      id: undefined
  }

  try {
    const response = await fetchWithAuth(
      `/api/v1/emon_host/add/`,
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

  return {success: true, redirect: `/emon-host`};
};

function AddEmonHost({
  is_dialog,
  successCallBack,
}: EditCrudComponentProps<EmonHostEdit>) {
  const { fetchWithAuth } = useAuth();
  return (
    <div>
      <EmonHostForm
        handleSubmit={(values: EmonHostFormType) => AddEmonHostAction(values, fetchWithAuth)}
        is_dialog={is_dialog}
        successCallBack={successCallBack}
      />
        
    </div>
  )
}

export default AddEmonHost

