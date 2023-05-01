from pytest_mock import MockerFixture

from agents_playground.agents.default.default_agent_identity import DefaultAgentIdentity

class TestAgentIdentity:
  def test_identity(self, mocker: MockerFixture) -> None:
    id_gen = mocker.Mock(return_value='SET')
    identity = DefaultAgentIdentity(id_generator = id_gen)
    
    assert id_gen.call_count == 4
    assert identity.id == 'SET'
    assert identity.render_id == 'SET'
    assert identity.toml_id == 'SET'
    assert identity.aabb_id == 'SET'