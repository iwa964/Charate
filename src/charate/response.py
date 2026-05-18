"""Response model implementations for character agents."""

from __future__ import annotations

from dataclasses import dataclass

from charate.profile import CharacterProfile
from charate.settings import normalize_language


@dataclass(frozen=True)
class RuleBasedCharacterModel:
    """Local fallback model for development and tests.

    Production apps can provide an on-device or user-configured LLM by
    implementing the ``ResponseModel`` protocol in ``charate.agent``.
    """

    output_language: str = "en"

    def generate(self, profile: CharacterProfile, user_input: str, memory_context: str = "") -> str:
        tone_hint = profile.personality.split(".")[0].strip() or profile.personality
        memory_line = (
            f" {_localized_response(self.output_language, 'memory_label')}: {memory_context.splitlines()[0].lstrip('- ')}"
            if memory_context
            else ""
        )
        return f"{profile.name}: {tone_hint}. {self._respond_to(user_input)}{memory_line}"

    def _respond_to(self, user_input: str) -> str:
        lowered = user_input.lower()
        if any(word in lowered for word in ("hello", "hi", "hey")):
            return _localized_response(self.output_language, "greeting")
        if "remind" in lowered:
            return _localized_response(self.output_language, "reminder")
        if "alarm" in lowered:
            return _localized_response(self.output_language, "alarm")
        return _localized_response(self.output_language, "fallback")


_LOCALIZED_RESPONSES: dict[str, dict[str, str]] = {
    "en": {
        "greeting": "I'm happy you came by.",
        "reminder": "I can keep that as a local reminder once the reminder module is enabled.",
        "alarm": "Alarms should live in an optional local extension, separate from my core memory.",
        "fallback": "Tell me more, and I'll answer in my own way.",
        "memory_label": "I remember",
    },
    "es": {
        "greeting": "Me alegra que hayas venido.",
        "reminder": "Puedo guardarlo como recordatorio local cuando se active el módulo de recordatorios.",
        "alarm": "Las alarmas deben vivir en una extensión local opcional, separadas de mi memoria central.",
        "fallback": "Cuéntame más y responderé a mi manera.",
        "memory_label": "Recuerdo",
    },
    "fr": {
        "greeting": "Je suis heureux que tu sois passé.",
        "reminder": "Je pourrai garder cela comme rappel local quand le module de rappels sera activé.",
        "alarm": "Les alarmes doivent rester dans une extension locale facultative, séparée de ma mémoire principale.",
        "fallback": "Dis-m'en plus, et je répondrai à ma façon.",
        "memory_label": "Je me souviens",
    },
    "de": {
        "greeting": "Ich freue mich, dass du vorbeigekommen bist.",
        "reminder": "Ich kann das als lokale Erinnerung behalten, sobald das Erinnerungsmodul aktiviert ist.",
        "alarm": "Alarme sollten in einer optionalen lokalen Erweiterung bleiben, getrennt von meinem Kernspeicher.",
        "fallback": "Erzähl mir mehr, und ich antworte auf meine eigene Weise.",
        "memory_label": "Ich erinnere mich",
    },
    "it": {
        "greeting": "Sono felice che tu sia passato.",
        "reminder": "Posso conservarlo come promemoria locale quando il modulo promemoria sarà abilitato.",
        "alarm": "Le sveglie dovrebbero vivere in un'estensione locale opzionale, separate dalla mia memoria principale.",
        "fallback": "Dimmi di più e risponderò a modo mio.",
        "memory_label": "Ricordo",
    },
    "ja": {
        "greeting": "来てくれてうれしいです。",
        "reminder": "リマインダーモジュールが有効になったら、ローカルのリマインダーとして覚えておけます。",
        "alarm": "アラームは私の中心的な記憶とは別の、任意のローカル拡張に置くべきです。",
        "fallback": "もっと聞かせてください。私らしく答えます。",
        "memory_label": "覚えています",
    },
    "ko": {
        "greeting": "와 줘서 기뻐요.",
        "reminder": "알림 모듈이 활성화되면 그것을 로컬 알림으로 기억할 수 있어요.",
        "alarm": "알람은 내 핵심 기억과 분리된 선택적 로컬 확장에 있어야 해요.",
        "fallback": "더 말해 주세요. 제 방식으로 답할게요.",
        "memory_label": "기억해요",
    },
    "pt": {
        "greeting": "Fico feliz que você tenha vindo.",
        "reminder": "Posso guardar isso como um lembrete local quando o módulo de lembretes estiver ativado.",
        "alarm": "Alarmes devem ficar em uma extensão local opcional, separados da minha memória central.",
        "fallback": "Conte-me mais, e responderei do meu jeito.",
        "memory_label": "Eu me lembro",
    },
    "zh": {
        "greeting": "很高兴你来了。",
        "reminder": "提醒模块启用后，我可以把它保存为本地提醒。",
        "alarm": "闹钟应该放在可选的本地扩展中，与我的核心记忆分开。",
        "fallback": "多告诉我一些，我会用自己的方式回答。",
        "memory_label": "我记得",
    },
}


def _localized_response(language: str, intent: str) -> str:
    code = normalize_language(language)
    return _LOCALIZED_RESPONSES.get(code, _LOCALIZED_RESPONSES["en"])[intent]
