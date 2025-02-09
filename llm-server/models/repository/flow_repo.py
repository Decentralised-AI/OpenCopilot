from typing import Optional, Type

from opencopilot_db import engine
from sqlalchemy.orm import sessionmaker

from shared.models.opencopilot_db.flow import Flow
from shared.models.opencopilot_db.flow_variables import FlowVariable

Session = sessionmaker(bind=engine)


def create_flow(chatbot_id: str, name: str, payload: dict, description: str = None) -> Flow:
    """
    Creates a new flow record in the database.

    Args:
        description:
        payload:
        chatbot_id: The ID of the chatbot associated with the flow.
        name: The name of the flow.

    Returns:
        The newly created Flow object.
    """
    with Session() as session:
        flow = Flow(chatbot_id=chatbot_id, name=name, payload=payload, description=description)
        session.add(flow)
        session.commit()
        session.refresh(flow)  # Refresh the instance to load any unloaded attributes
        return flow


def update_flow(flow_id: str, name: str, payload: dict, description: str) -> Optional[Flow]:
    """
    Updates an existing flow record in the database.

    Args:
        flow_id: The ID of the flow to update.
        name: The new name of the flow.
        payload: The new payload for the flow.
        description: The new description of the flow.

    Returns:
        The updated Flow object, or None if not found.
    """
    with Session() as session:
        flow = session.query(Flow).filter(Flow.id == flow_id).first()
        if flow:
            flow.name = name
            flow.payload = payload
            flow.description = description
            session.commit()
            session.refresh(flow)
            return flow
        return None


def get_all_flows_for_bot(bot_id: str) -> list[Type[Flow]]:
    """
    Retrieves all flows for a given bot from the database.

    Args:
        bot_id: The ID of the bot.

    Returns:
        A list of Flow objects.
    """
    with Session() as session:
        flows = session.query(Flow).filter(Flow.chatbot_id == bot_id).all()
        return flows


def get_flow_by_id(flow_id: str) -> Optional[Flow]:
    """
    Retrieves a specific flow by its ID from the database.

    Args:
        flow_id: The ID of the flow.

    Returns:
        The Flow object if found, otherwise None.
    """
    with Session() as session:
        return session.query(Flow).filter(Flow.id == str(flow_id)).first()


def get_variables_for_flow(flow_id: str) -> list[Type[FlowVariable]]:
    """
    Retrieves all variables for a specific flow from the database.

    Args:
        flow_id: The ID of the flow.

    Returns:
        A list of FlowVariable objects.
    """
    with Session() as session:
        return session.query(FlowVariable).filter(FlowVariable.flow_id == flow_id).all()


def add_or_update_variable_in_flow(bot_id: str, flow_id: str, name: str, value: str, runtime_override_key: str = None,
                                   runtime_override_action_id: str = None) -> FlowVariable:
    """
    Adds a new variable to a flow or updates it if it already exists.

    Args:
        bot_id:
        runtime_override_key:
        runtime_override_action_id:
        flow_id: The ID of the flow.
        name: The name of the variable.
        value: The value of the variable.

    Returns:
        The updated or newly created FlowVariable object.
    """
    with Session() as session:
        variable = session.query(FlowVariable).filter_by(bot_id=bot_id, flow_id=flow_id, name=name,
                                                         runtime_override_action_id=runtime_override_action_id,
                                                         runtime_override_key=runtime_override_key).first()
        if variable:
            variable.value = value
        else:
            variable = FlowVariable(bot_id=bot_id, flow_id=flow_id, name=name,
                                    runtime_override_action_id=runtime_override_action_id,
                                    runtime_override_key=runtime_override_key)
            session.add(variable)
        session.commit()
        return variable
