import { PromiseFormActionType } from "@/lib/types";
import { CategoryForm, CategoryFormType } from "./form";
import { useAuth } from "@/hooks/use-auth";
import { requestCatchError, requestErrorResponse } from "@/helpers/formActions";

const AddCategoryAction = async(
  values: CategoryFormType,
  fetchWithAuth: (input: RequestInfo, init?: RequestInit) => Promise<Response>
): PromiseFormActionType => {
  
  const data = {
      ...values,
      id: undefined
  }
  const requestTitle = "Add Category";
  const redirect = `/category`;
  try {
    const response = await fetchWithAuth(
      `/api/v1/category/add/`,
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
    console.log('Error fetching data:', error);
    return requestCatchError(error, requestTitle)
  }
};

type AddCategoryProps = {
  is_dialog?: boolean,
  successCallBack?: () => void
}

function AddCategory({
  is_dialog,
  successCallBack
}: AddCategoryProps) {
  const { fetchWithAuth } = useAuth();
  return (
    <div>
      <CategoryForm
        handleSubmit={(values: CategoryFormType) => AddCategoryAction(values, fetchWithAuth)}
        is_dialog={is_dialog}
        successCallBack={successCallBack}
      />
    </div>
  )
}

export default AddCategory

