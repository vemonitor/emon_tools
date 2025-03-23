import { PromiseFormActionType, EditCrudComponentProps, EmonHostEdit } from "@/lib/types";
import { EmonHostForm, EmonHostFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const AddEmonHostAction = async(
  values: EmonHostFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): PromiseFormActionType => {

  const data = {
      ...values,
      id: undefined
  }
  const requestTitle = "Add Emoncms Host";
  const redirect = `/emon-host`;
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
    return requestErrorResponse(
      response,
      requestTitle,
      redirect
    )
  } catch (error: unknown) {
    return requestCatchError(error, requestTitle)
  }
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

